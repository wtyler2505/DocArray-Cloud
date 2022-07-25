from dataclasses import dataclass, field
from typing import (
    Iterable,
    Dict,
    Optional,
    TYPE_CHECKING,
    Union,
    Any,
    Tuple,
    List,
)

from .... import Document
import numpy as np
from ..base.backend import BaseBackendMixin, TypeMap
from redis import Redis
from redis.exceptions import ResponseError
from redis.commands.search.field import VectorField, TextField, NumericField
from ....helper import dataclass_from_dict

if TYPE_CHECKING:
    from ....typing import DocumentArraySourceType
    from ....typing import DocumentArraySourceType, ArrayType


@dataclass
class RedisConfig:
    n_dim: int
    host: Optional[str] = field(default='localhost')
    port: Optional[int] = field(default=6379)
    flush: Optional[bool] = field(default=False)
    update_schema: Optional[bool] = field(default=True)
    distance: Optional[str] = field(default='COSINE')
    redis_config: Dict[str, Any] = field(default_factory=dict)
    index_text: Optional[bool] = field(default=False)
    tag_indices: List[str] = field(default_factory=list)
    batch_size: Optional[int] = field(default=64)
    method: Optional[str] = field(default='HNSW')
    initial_cap: Optional[int] = None
    ef_construction: Optional[int] = None
    m: Optional[int] = None
    ef_runtime: Optional[int] = None
    block_size: Optional[int] = None
    columns: Optional[List[Tuple[str, str]]] = None


class BackendMixin(BaseBackendMixin):
    """Provide necessary functions to enable this storage backend."""

    TYPE_MAP = {
        'str': TypeMap(type='text', converter=TextField),
        'bytes': TypeMap(type='text', converter=TextField),
        'int': TypeMap(type='integer', converter=NumericField),
        'float': TypeMap(type='float', converter=NumericField),
        'double': TypeMap(type='double', converter=NumericField),
        'long': TypeMap(type='long', converter=NumericField),
        # TODO add bool
    }

    def _init_storage(
        self,
        _docs: Optional['DocumentArraySourceType'] = None,
        config: Optional[Union[RedisConfig, Dict]] = None,
        **kwargs,
    ):
        if not config:
            raise RedisConfig()
        elif isinstance(config, dict):
            config = dataclass_from_dict(RedisConfig, config)

        if not config.distance in ['L2', 'IP', 'COSINE']:
            raise ValueError(f'Distance metric {config.distance} not supported')
        if not config.method in ['HNSW', 'FLAT']:
            raise ValueError(f'Method {config.method} not supported')

        self._offset2id_key = 'offset2id'
        self._config = config
        self.n_dim = self._config.n_dim
        self._config.columns = self._normalize_columns(self._config.columns)

        self._client = self._build_client()
        super()._init_storage(_docs, config, **kwargs)

        if _docs is None:
            return
        elif isinstance(_docs, Iterable):
            self.extend(_docs)
        elif isinstance(_docs, Document):
            self.append(_docs)

    def _build_client(self):
        client = Redis(
            host=self._config.host,
            port=self._config.port,
            **self._config.redis_config,
        )

        if self._config.flush:
            client.flushdb()

        # redis client will throw error if index does not exist
        if self._config.update_schema:
            try:
                client.ft().dropindex('idx')
            except ResponseError:
                pass

        if self._config.flush or self._config.update_schema:
            schema = self._build_schema_from_redis_config(self._config)
            client.ft().create_index(schema)

        return client

    def _build_schema_from_redis_config(self, redis_config):
        index_param = {
            'TYPE': 'FLOAT32',
            'DIM': self.n_dim,
            'DISTANCE_METRIC': self._config.distance,
        }

        if self._config.method == 'HNSW' and (
            self._config.m or self._config.ef_construction or self._config.ef_runtime
        ):
            index_options = {
                'M': self._config.m or 16,
                'EF_CONSTRUCTION': self._config.ef_construction or 200,
                'EF_RUNTIME': self._config.ef_runtime or 10,
            }
            index_param.update(index_options)

        if self._config.method == 'FLAT' and self._config.block_size:
            index_options = {'BLOCK_SIZE': self._config.block_size}
            index_param.update(index_options)

        if self._config.initial_cap:
            index_param['INITIAL_CAP'] = self._config.initial_cap
        schema = [VectorField('embedding', self._config.method, index_param)]

        if redis_config.tag_indices:
            for index in redis_config.tag_indices:
                # TODO TextField or TagField
                schema.append(TextField(index))

        # TODO whether to add schema to column (elastic does but qdrant doesn't)
        for col, coltype in self._config.columns:
            schema.append(self._map_column(col, coltype))
        return schema

    def _doc_id_exists(self, doc_id):
        return self._client.exists(doc_id)

    def _map_embedding(self, embedding: 'ArrayType') -> bytes:
        if embedding is not None:
            from ....math.ndarray import to_numpy_array

            embedding = to_numpy_array(embedding)

            if embedding.ndim > 1:
                embedding = np.asarray(embedding).squeeze()
        else:
            embedding = np.zeros(self.n_dim)
        return embedding.astype(np.float32).tobytes()

    def _get_offset2ids_meta(self) -> List:
        """Return the offset2ids stored in redis

        :return: a list containing ids

        :raises ValueError: error is raised if index _client is not found or no offsets are found
        """
        if not self._client:
            raise ValueError('Redis client does not exist')

        if not self._client.exists(self._offset2id_key):
            return []
        return self._client.lrange(self._offset2id_key, 0, -1)

    def _update_offset2ids_meta(self):
        """Update the offset2ids in redis"""
        if self._client.exists(self._offset2id_key):
            self._client.delete(self._offset2id_key)
        if len(self._offset2ids.ids) > 0:
            self._client.rpush(self._offset2id_key, *self._offset2ids.ids)
