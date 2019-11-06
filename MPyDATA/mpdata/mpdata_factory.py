"""
Created at 21.10.2019

@author: Piotr Bartman
@author: Michael Olesik
@author: Sylwester Arabas
"""

import numpy as np
from MPyDATA.mpdata.fields import ScalarField, VectorField
from MPyDATA.mpdata.mpdata import MPDATA
from MPyDATA.mpdata.eulerian_fields import EulerianFields


class MPDATAFactory:
    @staticmethod
    def mpdata(state: ScalarField, courant_field: VectorField, n_iters):
        assert state.data.shape[0] == courant_field.data[0].shape[0] + 1
        assert state.data.shape[1] == courant_field.data[0].shape[1] + 2
        assert courant_field.data[0].shape[0] == courant_field.data[1].shape[0] + 1
        assert courant_field.data[0].shape[1] == courant_field.data[1].shape[1] - 1
        # TODO assert halo

        prev = state.clone()
        C_antidiff = courant_field.clone()
        flux = courant_field.clone()
        halo = state.halo
        mpdata = MPDATA(curr=state, prev=prev, C_physical=courant_field, C_antidiff=C_antidiff, flux=flux,
                        n_iters=n_iters, halo=halo)

        return mpdata

    @staticmethod
    def kinematic_2d(grid, size, dt, stream_function: callable, field_values: dict, halo=1):
        courant_field = nondivergent_vector_field_2d(grid, size, halo, dt, stream_function)

        mpdatas = {}
        for key, value in field_values.items():
            state = uniform_scalar_field(grid, value, halo)
            mpdatas[key] = MPDATAFactory.mpdata(state=state, courant_field=courant_field, n_iters=1)

        eulerian_fields = EulerianFields(mpdatas)
        return courant_field, eulerian_fields


def uniform_scalar_field(grid, value, halo):
    data = np.full(grid, value)
    scalar_field = ScalarField(data=data, halo=halo)
    return scalar_field


def x_vec_coord(grid, size):
    nx = grid[0]+1
    nz = grid[1]
    xX = np.repeat(np.linspace(0, size[0], nx).reshape((nx, 1)), nz, axis=1)
    assert xX.shape == (nx, nz)
    zZ = np.repeat(np.linspace(1 / 2, size[1] - 1/2, nz).reshape((1, nz)), nx, axis=0)
    assert zZ.shape == (nx, nz)
    return xX, zZ


def z_vec_coord(grid, size):
    nx = grid[0]
    nz = grid[1]+1
    xX = np.repeat(np.linspace(1/2, size[0]-1/2, nx).reshape((nx, 1)), nz, axis=1)
    assert xX.shape == (nx, nz)
    zZ = np.repeat(np.linspace(0, size[1], nz).reshape((1, nz)), nx, axis=0)
    assert zZ.shape == (nx, nz)
    return xX, zZ


def nondivergent_vector_field_2d(grid, size, halo, dt, stream_function: callable):
    # TODO: density!
    dx = size[0] / grid[0]
    dz = size[1] / grid[1]

    xX, zZ = x_vec_coord(grid, size)
    velocity_x = -(stream_function(xX, zZ + 1/2) - stream_function(xX, zZ - 1/2)) / dz

    xX, zZ = z_vec_coord(grid, size)
    velocity_z = (stream_function(xX + dx / 2, zZ) - stream_function(xX - 1/2, zZ)) / dx

    courant_field = [velocity_x * dt / dx, velocity_z * dt / dz]

    # CFL condition
    for d in range(len(courant_field)):
        np.testing.assert_array_less(np.abs(courant_field[d]), 1)

    result = VectorField(data=courant_field, halo=halo)

    # nondivergence (of velocity field, hence dt)
    assert np.amax(abs(result.div(grid_step=[dt, dt]).data)) < 5e-9

    return result
