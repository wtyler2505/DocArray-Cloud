from pathlib import Path

import numpy as np
import pytest
from pydantic.tools import parse_obj_as, schema_json_of

from docarray.document.io.json import orjson_dumps
from docarray.typing import PointCloudUrl

REPO_ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent.absolute()
TOYDATA_DIR = REPO_ROOT_DIR / 'tests' / 'toydata'

MESH_FILES = {
    'obj': str(TOYDATA_DIR / 'tetrahedron.obj'),
    'glb': str(TOYDATA_DIR / 'test.glb'),
    'ply': str(TOYDATA_DIR / 'cube.ply'),
}
REMOTE_OBJ_FILE = 'https://people.sc.fsu.edu/~jburkardt/data/obj/al.obj'


@pytest.mark.slow
@pytest.mark.internet
@pytest.mark.parametrize(
    'file_format, file_path',
    [
        ('obj', MESH_FILES['obj']),
        ('glb', MESH_FILES['glb']),
        ('ply', MESH_FILES['ply']),
        ('remote-obj', REMOTE_OBJ_FILE),
    ],
)
def test_load(file_format, file_path):
    n_samples = 100
    url = parse_obj_as(PointCloudUrl, file_path)
    point_cloud = url.load(samples=n_samples)

    assert isinstance(point_cloud, np.ndarray)
    assert point_cloud.shape == (n_samples, 3)


@pytest.mark.slow
@pytest.mark.internet
@pytest.mark.parametrize(
    'file_format, file_path',
    [
        ('obj', MESH_FILES['obj']),
        ('glb', MESH_FILES['glb']),
        ('ply', MESH_FILES['ply']),
        ('remote-obj', REMOTE_OBJ_FILE),
    ],
)
def test_load_with_multiple_geometries_true(file_format, file_path):
    n_samples = 100
    url = parse_obj_as(PointCloudUrl, file_path)
    point_cloud = url.load(samples=n_samples, multiple_geometries=True)

    assert isinstance(point_cloud, np.ndarray)
    assert len(point_cloud.shape) == 3
    assert point_cloud.shape[1:] == (100, 3)


def test_json_schema():
    schema_json_of(PointCloudUrl)


def test_dump_json():
    url = parse_obj_as(PointCloudUrl, REMOTE_OBJ_FILE)
    orjson_dumps(url)
