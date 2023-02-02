import numpy as np
import pytest
import tensorflow as tf
from pydantic import schema_json_of
from pydantic.tools import parse_obj_as
from tensorflow.python.framework.errors_impl import InvalidArgumentError

from docarray.base_document.io.json import orjson_dumps
from docarray.typing import TensorFlowTensor


def test_json_schema():
    schema_json_of(TensorFlowTensor)


def test_dump_json():
    tensor = parse_obj_as(TensorFlowTensor, tf.zeros((3, 224, 224)))
    orjson_dumps(tensor)


def test_unwrap():
    tf_tensor = parse_obj_as(TensorFlowTensor, tf.zeros((3, 224, 224)))
    unwrapped = tf_tensor.unwrap()

    assert not isinstance(unwrapped, TensorFlowTensor)
    assert isinstance(tf_tensor, TensorFlowTensor)
    assert isinstance(unwrapped, tf.Tensor)

    assert np.allclose(unwrapped, np.zeros((3, 224, 224)))


def test_from_ndarray():
    nd = np.array([1, 2, 3])
    tensor = TensorFlowTensor.from_ndarray(nd)
    assert isinstance(tensor, TensorFlowTensor)
    assert isinstance(tensor.tensor, tf.Tensor)


def test_parametrized():
    # correct shape, single axis
    tf_tensor = parse_obj_as(TensorFlowTensor[128], tf.zeros(128))
    assert isinstance(tf_tensor, TensorFlowTensor)
    assert isinstance(tf_tensor.tensor, tf.Tensor)
    assert tf_tensor.tensor.shape == (128,)

    # correct shape, multiple axis
    tf_tensor = parse_obj_as(TensorFlowTensor[3, 224, 224], tf.zeros((3, 224, 224)))
    assert isinstance(tf_tensor, TensorFlowTensor)
    assert isinstance(tf_tensor.tensor, tf.Tensor)
    assert tf_tensor.tensor.shape == (3, 224, 224)

    # wrong but reshapable shape
    tf_tensor = parse_obj_as(TensorFlowTensor[3, 224, 224], tf.zeros((224, 3, 224)))
    assert isinstance(tf_tensor, TensorFlowTensor)
    assert isinstance(tf_tensor.tensor, tf.Tensor)
    assert tf_tensor.tensor.shape == (3, 224, 224)

    # wrong and not reshapable shape
    with pytest.raises(InvalidArgumentError):
        parse_obj_as(TensorFlowTensor[3, 224, 224], tf.zeros((224, 224)))


def test_parametrized_with_str():
    # test independent variable dimensions
    tf_tensor = parse_obj_as(TensorFlowTensor[3, 'x', 'y'], tf.zeros((3, 224, 224)))
    assert isinstance(tf_tensor, TensorFlowTensor)
    assert isinstance(tf_tensor.tensor, tf.Tensor)
    assert tf_tensor.tensor.shape == (3, 224, 224)

    tf_tensor = parse_obj_as(TensorFlowTensor[3, 'x', 'y'], tf.zeros((3, 60, 128)))
    assert isinstance(tf_tensor, TensorFlowTensor)
    assert isinstance(tf_tensor.tensor, tf.Tensor)
    assert tf_tensor.tensor.shape == (3, 60, 128)

    with pytest.raises(ValueError):
        parse_obj_as(TensorFlowTensor[3, 'x', 'y'], tf.zeros((4, 224, 224)))

    with pytest.raises(ValueError):
        parse_obj_as(TensorFlowTensor[3, 'x', 'y'], tf.zeros((100, 1)))

    # test dependent variable dimensions
    tf_tensor = parse_obj_as(TensorFlowTensor[3, 'x', 'x'], tf.zeros((3, 224, 224)))
    assert isinstance(tf_tensor, TensorFlowTensor)
    assert isinstance(tf_tensor.tensor, tf.Tensor)
    assert tf_tensor.tensor.shape == (3, 224, 224)

    with pytest.raises(ValueError):
        _ = parse_obj_as(TensorFlowTensor[3, 'x', 'x'], tf.zeros((3, 60, 128)))

    with pytest.raises(ValueError):
        _ = parse_obj_as(TensorFlowTensor[3, 'x', 'x'], tf.zeros((3, 60)))


@pytest.mark.parametrize('shape', [(3, 224, 224), (224, 224, 3)])
def test_parameterized_tensor_class_name(shape):
    MyTFT = TensorFlowTensor[3, 224, 224]
    tensor = parse_obj_as(MyTFT, tf.zeros(shape))

    assert MyTFT.__name__ == 'TensorFlowTensor[3, 224, 224]'
    assert MyTFT.__qualname__ == 'TensorFlowTensor[3, 224, 224]'

    assert tensor.__class__.__name__ == 'TensorFlowTensor'
    assert tensor.__class__.__qualname__ == 'TensorFlowTensor'
    assert f'{tensor.tensor[0][0][0]}' == '0.0'


def test_parametrized_subclass():
    c1 = TensorFlowTensor[128]
    c2 = TensorFlowTensor[128]
    assert issubclass(c1, c2)
    assert issubclass(c1, TensorFlowTensor)

    assert not issubclass(c1, TensorFlowTensor[256])


def test_parametrized_instance():
    t = parse_obj_as(TensorFlowTensor[128], tf.zeros((128,)))
    assert isinstance(t, TensorFlowTensor[128])
    assert isinstance(t, TensorFlowTensor)
    # assert isinstance(t, tf.Tensor)

    assert not isinstance(t, TensorFlowTensor[256])
    assert not isinstance(t, TensorFlowTensor[2, 128])
    assert not isinstance(t, TensorFlowTensor[2, 2, 64])


def test_parametrized_equality():
    t1 = parse_obj_as(TensorFlowTensor[128], tf.zeros((128,)))
    t2 = parse_obj_as(TensorFlowTensor[128], tf.zeros((128,)))
    assert tf.experimental.numpy.allclose(t1.tensor, t2.tensor)


def test_parametrized_operations():
    t1 = parse_obj_as(TensorFlowTensor[128], tf.zeros((128,)))
    t2 = parse_obj_as(TensorFlowTensor[128], tf.zeros((128,)))
    t_result = t1.tensor + t2.tensor
    assert isinstance(t_result, tf.Tensor)
    assert not isinstance(t_result, TensorFlowTensor)
    assert not isinstance(t_result, TensorFlowTensor[128])
