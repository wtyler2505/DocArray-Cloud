import io
import logging
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Type

import boto3
import botocore
from smart_open import open
from typing_extensions import TYPE_CHECKING

from docarray.array.array.pushpull.helpers import _from_binary_stream, _to_binary_stream
from docarray.array.array.pushpull.pushpull import __cache_path__

if TYPE_CHECKING:  # pragma: no cover
    from docarray import BaseDocument, DocumentArray


class _BufferedCachingReader:
    """A buffered reader that writes to a cache file while reading."""

    def __init__(
        self, iter_bytes: io.BufferedReader, cache_path: Optional['Path'] = None
    ):
        self._data = iter_bytes
        self._cache = None
        if cache_path:
            self._cache_path = cache_path.with_suffix('.tmp')
            self._cache = open(self._cache_path, 'wb')
        self.closed = False

    def read(self, size: Optional[int] = -1) -> bytes:
        bytes = self._data.read(size)
        if self._cache:
            self._cache.write(bytes)
        return bytes

    def close(self):
        if not self.closed and self._cache:
            self._cache_path.rename(self._cache_path.with_suffix('.da'))
            self._cache.close()


class PushPullS3:
    """Class to push and pull DocumentArray to and from S3."""

    @staticmethod
    def list(namespace: str, show_table: bool = False) -> List[str]:
        """List all DocumentArrays in the specified bucket and namespace.

        :param namespace: The bucket and namespace to list. e.g. my_bucket/my_namespace
        :param show_table: If true, a rich table will be printed to the console.
        :return: A list of DocumentArray names.
        """
        bucket, namespace = namespace.split('/', 1)
        s3 = boto3.resource('s3')
        s3_bucket = s3.Bucket(bucket)
        da_files = [
            obj
            for obj in s3_bucket.objects.all()
            if obj.key.startswith(namespace) and obj.key.endswith('.da')
        ]
        da_names = [f.key.split('/')[-1].split('.')[0] for f in da_files]

        if show_table:
            from rich import box, filesize
            from rich.console import Console
            from rich.table import Table

            table = Table(
                title=f'You have {len(da_files)} DocumentArrays in bucket s3://{bucket} under the namespace "{namespace}"',
                box=box.SIMPLE,
                highlight=True,
            )
            table.add_column('Name')
            table.add_column('Last Modified', justify='center')
            table.add_column('Size')

            for da_name, da_file in zip(da_names, da_files):
                table.add_row(
                    da_name,
                    str(da_file.last_modified),
                    str(filesize.decimal(da_file.size)),
                )

            Console().print(table)
        return da_names

    @staticmethod
    def delete(name: str, missing_ok: bool = True) -> bool:
        """Delete the DocumentArray object at the specified bucket and key.

        :param name: The bucket and key to delete. e.g. my_bucket/my_key
        :param missing_ok: If true, no error will be raised if the object does not exist.
        :return: True if the object was deleted, False if it did not exist.
        """
        bucket, name = name.split('/', 1)
        s3 = boto3.resource('s3')
        object = s3.Object(bucket, name + '.da')
        try:
            object.load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                if missing_ok:
                    return False
                else:
                    raise ValueError(f'Object {name} does not exist')
            else:
                raise
        object.delete()
        return True

    @staticmethod
    def push(
        da: 'DocumentArray',
        name: str,
        public: bool = False,
        show_progress: bool = False,
        branding: Optional[Dict] = None,
    ) -> Dict:
        """Push this DocumentArray object to the specified bucket and key.

        :param docs: a stream of documents
        :param name: The bucket and key to push to. e.g. my_bucket/my_key
        :param public: Not used by the ``s3`` protocol.
        :param show_progress: If true, a progress bar will be displayed.
        :param branding: Not used by the ``s3`` protocol.
        """
        return PushPullS3.push_stream(iter(da), name, public, show_progress, branding)

    @staticmethod
    def push_stream(
        docs: Iterator['BaseDocument'],
        name: str,
        public: bool = True,
        show_progress: bool = False,
        branding: Optional[Dict] = None,
    ) -> Dict:
        """Push a stream of documents to the specified bucket and key.

        :param docs: a stream of documents
        :param name: The bucket and key to push to. e.g. my_bucket/my_key
        :param public: Not used by the ``s3`` protocol.
        :param show_progress: If true, a progress bar will be displayed.
        :param branding: Not used by the ``s3`` protocol.
        """
        if branding is not None:
            logging.warning("Branding is not supported for S3 push")

        bucket, name = name.split('/', 1)
        binary_stream = _to_binary_stream(
            docs, protocol='pickle', compress=None, show_progress=show_progress
        )

        # Upload to S3
        with open(
            f"s3://{bucket}/{name}.da",
            'wb',
            compression='.gz',
            transport_params={'multipart_upload': False},
        ) as fout:
            while True:
                try:
                    fout.write(next(binary_stream))
                except StopIteration:
                    break

        return {}

    @staticmethod
    def pull(
        cls: Type['DocumentArray'],
        name: str,
        show_progress: bool = False,
        local_cache: bool = False,
    ) -> 'DocumentArray':
        """Pull a :class:`DocumentArray` from the specified bucket and key.

        :param name: The bucket and key to pull from. e.g. my_bucket/my_key
        :param show_progress: if true, display a progress bar.
        :param local_cache: store the downloaded DocumentArray to local cache
        :return: a :class:`DocumentArray` object
        """
        da = cls(  # type: ignore
            PushPullS3.pull_stream(
                cls, name, show_progress=show_progress, local_cache=local_cache
            )
        )
        return da

    @staticmethod
    def pull_stream(
        cls: Type['DocumentArray'],
        name: str,
        show_progress: bool,
        local_cache: bool,
    ) -> Iterator['BaseDocument']:
        """Pull a stream of Documents from the specified name.
        Name is expected to be in the format of bucket/key.

        :param name: The bucket and key to pull from. e.g. my_bucket/my_key
        :param show_progress: if true, display a progress bar.
        :param local_cache: store the downloaded DocumentArray to local cache
        :return: An iterator of Documents
        """

        bucket, name = name.split('/', 1)

        save_name = name.replace('/', '_')
        cache_path = __cache_path__ / f'{save_name}.da'

        source = _BufferedCachingReader(
            open(f"s3://{bucket}/{name}.da", 'rb', compression='.gz'),
            cache_path=cache_path if local_cache else None,
        )

        if local_cache:
            if cache_path.exists():
                object_header = boto3.client('s3').head_object(
                    Bucket=bucket, Key=name + '.da'
                )
                if cache_path.stat().st_size == object_header['ContentLength']:
                    logging.info(
                        f'Using cached file for {name} (size: {cache_path.stat().st_size})'
                    )
                    source = open(cache_path, 'rb')

        return _from_binary_stream(
            cls.document_type,
            source,
            protocol='pickle',
            compress=None,
            show_progress=show_progress,
        )
