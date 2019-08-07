"""
Created at 31.07.2019

@author: Piotr Bartman
@author: Sylwester Arabas
"""

import pytest
import numpy as np

from SDM.backends.default import Default
from SDM.backends.numpy import Numpy
from SDM.backends.numba import Numba
from SDM.backends.numba_parallel import NumbaParallel
# from SDM.backends.thrustRTC import ThrustRTC

# noinspection PyUnresolvedReferences
from tests.backends.__parametrisation__ import shape_full, shape_1d, shape_2d, \
                                               dtype_full, dtype, \
                                               length, natural_length, \
                                               order


@pytest.mark.parametrize('sut', [Numpy, Numba, NumbaParallel])
class TestBackend:
    @staticmethod
    def data(backend, shape, dtype, seed=0):
        np.random.seed(seed)
        rand_ndarray = (100*np.random.rand(*shape)).astype(dtype)

        result_sut = backend.from_ndarray(rand_ndarray)
        result_default = Default.from_ndarray(rand_ndarray)

        return result_sut, result_default

    @staticmethod
    def idx_length(shape):
        if len(shape) >= 2:
            result = shape[1]
        else:
            result = shape[0]

        return result

    @staticmethod
    def idx(backend, shape, order, seed=0):
        np.random.seed(seed)

        idx_len = TestBackend.idx_length(shape)

        idx_ndarray = np.arange(idx_len)

        if order == 'desc':
            idx_ndarray = idx_ndarray[::-1]
        elif order == 'random':
            np.random.permutation(idx_ndarray)

        result_sut = backend.from_ndarray(idx_ndarray)
        result_default = Default.from_ndarray(idx_ndarray)

        return result_sut, result_default

    @staticmethod
    def length(length, shape):
        idx_len = TestBackend.idx_length(shape)

        if length == 'zero':
            return 0
        elif length == 'middle':
            return (idx_len + 1) // 2
        elif length == 'full':
            return idx_len

    @staticmethod
    def test_array(sut, dtype_full, shape_full):
        try:
            # Act
            actual = sut.array(shape_full, dtype_full)
            expected = Default.array(shape_full, dtype_full)

            # Assert
            assert sut.shape(actual) == Default.shape(expected)
            assert sut.dtype(actual) == Default.dtype(expected)
        except NotImplementedError:
            if dtype_full in (float, int):
                assert False

    @staticmethod
    def test_from_ndarray(sut, dtype_full, shape_full):
        # Arrange
        ndarray = np.empty(shape=shape_full, dtype=dtype_full)

        try:
            # Act
            actual = sut.from_ndarray(ndarray)
            expected = Default.from_ndarray(ndarray)

            # Assert
            np.testing.assert_array_equal(sut.to_ndarray(actual), Default.to_ndarray(expected))
        except NotImplementedError:
            if dtype_full in (float, int):
                assert False

    # TODO test_stack_2d(array_1, array_2, axis)

    # TODO test_get_item(array_1, array_2, axis)

    # TODO idx as input
    @staticmethod
    def test_shuffle(sut, shape_1d, natural_length):
        # Arrange
        axis = 0
        sut_data, data = TestBackend.data(sut, shape_1d, int)
        sut_idx, idx = TestBackend.idx(sut, shape_1d, 'asc')
        length = TestBackend.length(natural_length, shape_1d)
        # Act
        sut.shuffle(sut_data, length, axis)
        Default.shuffle(data, length, axis)

        # Assert
        sut_data_original, data_original = TestBackend.data(sut, shape_1d, int)
        assert sut.shape(sut_data) == Default.shape(data)
        assert sut.amin(sut_data, sut_idx, length) == sut.amin(sut_data_original, idx, length)
        assert sut.amax(sut_data, sut_idx, length) == sut.amax(sut_data_original, idx, length)

    @staticmethod
    def test_argsort(sut, shape_1d, length, order):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_1d, int)
        sut_idx, idx = TestBackend.idx(sut, shape_1d, order)
        length = TestBackend.length(length, shape_1d)

        # Act
        sut.argsort(sut_data, sut_idx, length)
        Default.argsort(data, idx, length)

        # Assert
        np.testing.assert_array_equal(sut.to_ndarray(sut_data), Default.to_ndarray(data))
        np.testing.assert_array_equal(sut.to_ndarray(sut_idx), Default.to_ndarray(idx))

    @staticmethod
    def test_stable_argsort(sut, shape_1d, dtype, length, order):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_1d, dtype)
        sut_idx, idx = TestBackend.idx(sut, shape_1d, order)
        length = TestBackend.length(length, shape_1d)

        # Act
        sut.stable_argsort(sut_data, sut_idx, length)
        Default.stable_argsort(data, idx, length)

        # Assert
        np.testing.assert_array_equal(sut.to_ndarray(sut_data), Default.to_ndarray(data))
        np.testing.assert_array_equal(sut.to_ndarray(sut_idx), Default.to_ndarray(idx))

    @staticmethod
    def test_amin(sut, shape_1d, natural_length, order):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_1d, float)
        sut_idx, idx = TestBackend.idx(sut, shape_1d, order)
        length = TestBackend.length(natural_length, shape_1d)


        # Act
        actual = sut.amin(sut_data, sut_idx, length)
        expected = Default.amin(data, idx, length)

        # Assert
        assert actual == expected

    @staticmethod
    def test_amax(sut, shape_1d, natural_length, order):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_1d, float)
        sut_idx, idx = TestBackend.idx(sut, shape_1d, order)
        length = TestBackend.length(natural_length, shape_1d)

        # Act
        actual = sut.amax(sut_data, sut_idx, length)
        expected = Default.amax(data, idx, length)

        # Assert
        assert actual == expected

    @staticmethod
    def test_shape(sut, shape_full, dtype):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_full, dtype)

        # Act
        actual = sut.shape(sut_data)
        expected = Default.shape(data)

        # Assert
        assert actual == expected

    @staticmethod
    def test_dtype(sut, shape_full, dtype):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_full, dtype)

        # Act
        actual = sut.dtype(sut_data)
        expected = Default.dtype(data)

        # Assert
        assert actual == expected

    @staticmethod
    def test_urand(sut, shape_1d):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_1d, float)
        sut_idx, idx = TestBackend.idx(sut, shape_1d, 'asc')
        length = shape_1d[0]

        # Act
        sut.urand(sut_data)
        Default.urand(data)

        # Assert
        assert sut.shape(sut_data) == Default.shape(data)
        assert sut.dtype(sut_data) == Default.dtype(data)
        assert sut.amin(sut_data, sut_idx, length) >= 0
        assert sut.amax(sut_data, idx, length) <= 1

    @staticmethod
    @pytest.mark.parametrize('data_ndarray', [
        np.array([0] * 87),
        np.array([1, 0, 1, 0, 1, 1, 1, 1]),
        np.array([1, 1, 1, 1, 1, 0, 1, 0]),
        np.array([1] * 87)
    ])
    def test_remove_zeros(sut, data_ndarray, length, order):
        # Arrange
        shape = data_ndarray.shape
        sut_data = sut.from_ndarray(data_ndarray)
        data = Default.from_ndarray(data_ndarray)
        sut_idx, idx = TestBackend.idx(sut, shape, order)
        length = TestBackend.length(length, shape)

        # Act
        sut_new_length = sut.remove_zeros(sut_data, sut_idx, length)
        new_length = Default.remove_zeros(data, idx, length)

        # Assert
        assert sut_new_length == new_length
        np.testing.assert_array_equal(sut.to_ndarray(sut_data), Default.to_ndarray(data))
        np.testing.assert_array_equal(sut.to_ndarray(sut_idx)[sut_new_length:], Default.to_ndarray(idx)[new_length:])
        np.testing.assert_array_equal(sut.to_ndarray(sut_idx)[:sut_new_length].sort(),
                                      sut.to_ndarray(sut_idx)[:new_length].sort())

    @staticmethod
    def test_extensive_attr_coalescence(sut, shape_2d, natural_length, order):
        # Arrange
        sut_n, n = TestBackend.data(sut, (shape_2d[1],), int)
        sut_data, data = TestBackend.data(sut, shape_2d, float)
        sut_idx, idx = TestBackend.idx(sut, shape_2d, order)
        length = TestBackend.length(natural_length, shape_2d)

        assert Default.amin(n, idx, length) > 0

        sut_gamma = sut.from_ndarray(np.arange(shape_2d[1] // 2).astype(np.float64))
        gamma = Default.from_ndarray(np.arange(shape_2d[1] // 2).astype(np.float64))

        # Act
        sut.extensive_attr_coalescence(sut_n, sut_idx, length, sut_data, sut_gamma)
        Default.extensive_attr_coalescence(n, idx, length, data, gamma)

        # Assert
        np.testing.assert_array_equal(sut.to_ndarray(sut_n), Default.to_ndarray(n))
        np.testing.assert_array_equal(sut.to_ndarray(sut_idx), Default.to_ndarray(idx))
        np.testing.assert_array_equal(sut.to_ndarray(sut_data), Default.to_ndarray(data))
        np.testing.assert_array_equal(sut.to_ndarray(sut_gamma), Default.to_ndarray(gamma))

    @staticmethod
    # TODO new_n == 0
    def test_n_coalescence(sut, shape_1d, natural_length, order):
        # Arrange
        sut_n, n = TestBackend.data(sut, shape_1d, int)
        sut_idx, idx = TestBackend.idx(sut, shape_1d, order)
        length = TestBackend.length(natural_length, shape_1d)

        assert Default.amin(n, idx, length) > 0

        sut_gamma = sut.from_ndarray(np.arange(shape_1d[0] // 2).astype(np.float64))
        gamma = Default.from_ndarray(np.arange(shape_1d[0] // 2).astype(np.float64))

        # Act
        sut.n_coalescence(sut_n, sut_idx, length, sut_gamma)
        Default.n_coalescence(n, idx, length, gamma)

        # Assert
        np.testing.assert_array_equal(sut.to_ndarray(sut_n), Default.to_ndarray(n))
        np.testing.assert_array_equal(sut.to_ndarray(sut_idx), Default.to_ndarray(idx))
        np.testing.assert_array_equal(sut.to_ndarray(sut_gamma), Default.to_ndarray(gamma))

    @staticmethod
    def test_sum_pair(sut, shape_1d, length, order):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_1d, float)
        sut_data_in, data_in = TestBackend.data(sut, shape_1d, float, seed=1)
        sut_idx, idx = TestBackend.idx(sut, shape_1d, order)
        length = TestBackend.length(length, shape_1d)

        # Act
        sut.sum_pair(sut_data, sut_data_in, sut_idx, length)
        Default.sum_pair(data, data_in, idx, length)

        # Assert
        np.testing.assert_array_equal(sut.to_ndarray(sut_data), Default.to_ndarray(data))
        np.testing.assert_array_equal(sut.to_ndarray(sut_data_in), Default.to_ndarray(data_in))
        np.testing.assert_array_equal(sut.to_ndarray(sut_idx), Default.to_ndarray(idx))

    @staticmethod
    def test_max_pair(sut, shape_1d, length, order):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_1d, float)
        sut_data_in, data_in = TestBackend.data(sut, shape_1d, int, seed=1)
        sut_idx, idx = TestBackend.idx(sut, shape_1d, order)
        length = TestBackend.length(length, shape_1d)

        # Act
        sut.max_pair(sut_data, sut_data_in, sut_idx, length)
        Default.max_pair(data, data_in, idx, length)

        # Assert
        np.testing.assert_array_equal(sut.to_ndarray(sut_data), Default.to_ndarray(data))
        np.testing.assert_array_equal(sut.to_ndarray(sut_data_in), Default.to_ndarray(data_in))
        np.testing.assert_array_equal(sut.to_ndarray(sut_idx), Default.to_ndarray(idx))

    @staticmethod
    @pytest.mark.parametrize('multiplier', [0., 1., 87., -5., .7, -.44])
    def test_multiply_scalar(sut, shape_1d, multiplier):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_1d, float)

        # Act
        sut.multiply(sut_data, multiplier)
        Default.multiply(data, multiplier)

        # Assert
        np.testing.assert_array_equal(sut.to_ndarray(sut_data), Default.to_ndarray(data))

    @staticmethod
    def test_multiply_elementwise(sut, shape_1d):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_1d, float)
        sut_multiplier, multiplier = TestBackend.data(sut, shape_1d, float, seed=1)

        # Act
        sut.multiply(sut_data, sut_multiplier)
        Default.multiply(data, multiplier)

        # Assert
        np.testing.assert_array_equal(sut.to_ndarray(sut_data), Default.to_ndarray(data))
        np.testing.assert_array_equal(sut.to_ndarray(sut_multiplier), Default.to_ndarray(multiplier))

    @staticmethod
    def test_sum(sut, shape_1d):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_1d, float)
        sut_data_in, data_in = TestBackend.data(sut, shape_1d, float)

        # Act
        sut.sum(sut_data, sut_data_in)
        Default.sum(data, data_in)

        # Assert
        np.testing.assert_array_equal(sut.to_ndarray(sut_data), Default.to_ndarray(data))

    @staticmethod
    def test_floor(sut, shape_1d):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_1d, float)

        # Act
        sut.floor(sut_data)
        Default.floor(data)

        # Assert
        np.testing.assert_array_equal(sut.to_ndarray(sut_data), Default.to_ndarray(data))

    @staticmethod
    def test_to_ndarray(sut, shape_full, dtype):
        # Arrange
        sut_data, data = TestBackend.data(sut, shape_full, dtype)

        # Act
        actual = sut.to_ndarray(sut_data)
        expected = Default.to_ndarray(data)

        # Assert
        np.testing.assert_array_equal(actual, expected)