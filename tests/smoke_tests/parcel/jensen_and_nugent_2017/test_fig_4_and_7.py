# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
from pathlib import Path
import numpy as np
import pytest
from scipy import signal
from PySDM_examples.utils import notebook_vars
from PySDM_examples import Jensen_and_Nugent_2017
from PySDM.physics.constants import PER_CENT
from PySDM.physics import si
from .test_fig_3 import find_cloud_base_index, find_max_alt_index

PLOT = False
N_SD = Jensen_and_Nugent_2017.simulation.N_SD_NON_GCCN + np.count_nonzero(
    Jensen_and_Nugent_2017.table_3.NA
)


@pytest.fixture(scope="session", name="variables")
def variables_fixture():
    return notebook_vars(
        file=Path(Jensen_and_Nugent_2017.__file__).parent / "Fig_4_and_7.ipynb",
        plot=PLOT,
    )


class TestFig4And7:
    @staticmethod
    def test_height_range(variables):
        """note: in the plot the y-axis has cloud-base height subtracted, here not"""
        z_minus_z0 = (
            np.asarray(variables["output"]["products"]["z"]) - variables["settings"].z0
        )
        epsilon = 1 * si.m
        assert 0 <= min(z_minus_z0) < max(z_minus_z0) < 600 * si.m + epsilon

    @staticmethod
    def test_cloud_base_height(variables):
        cloud_base_index = find_cloud_base_index(variables["output"]["products"])
        z0 = variables["settings"].z0
        assert (
            290 * si.m
            < variables["output"]["products"]["z"][cloud_base_index] - z0
            < 300 * si.m
        )

    @staticmethod
    def test_supersaturation_maximum(variables):
        supersaturation = np.asarray(variables["output"]["products"]["S_max"])
        assert signal.argrelextrema(supersaturation, np.greater)[0].shape[0] == 1
        assert 0.4 * PER_CENT < np.nanmax(supersaturation) < 0.5 * PER_CENT

    class TestFig4:

        @staticmethod
        @pytest.mark.parametrize(
            "drop_id, activated, grow_on_descent",
            (
                [(drop_id, False, False) for drop_id in range(0, int(0.15 * N_SD))]
                + [
                    (drop_id, True, False)
                    for drop_id in range(int(0.25 * N_SD), int(0.6 * N_SD))
                ]
                + [(drop_id, True, True) for drop_id in range(int(0.777 * N_SD), N_SD)]
            ),
        )
        def test_grow_vs_evaporation_on_descent(
            variables, drop_id, activated, grow_on_descent
        ):
            # arrange
            cb_idx = find_cloud_base_index(variables["output"]["products"])
            ma_idx = find_max_alt_index(variables["output"]["products"])
            radii = variables["output"]["attributes"]["radius"][drop_id]
            r1 = radii[0]
            r2 = radii[cb_idx]
            r3 = radii[ma_idx]
            r4 = radii[-1]

            activated_actual = r1 < r2 < r3
            assert activated == activated_actual

            if grow_on_descent:
                assert r3 < r4
            else:
                assert r3 > r4

        @staticmethod
        def test_maximal_size_of_largest_droplet(variables):
            np.testing.assert_approx_equal(
                max(variables["output"]["attributes"]["radius"][-1]),
                57 * si.um,
                significant=2,
            )

        @staticmethod
        def test_initial_size_of_largest_droplet(variables):
            np.testing.assert_approx_equal(
                min(variables["output"]["attributes"]["radius"][-1]),
                19 * si.um,
                significant=2,
            )

    class TestFig7:
        @staticmethod
        @pytest.mark.parametrize(
            "mask_label,dry_radius_um, min_value, max_value",
            (
                ("ascent", 0.1, 0, 0.1 * PER_CENT),
                ("ascent", 2, -0.75 * PER_CENT, 0),
                ("ascent", 9, -2 * PER_CENT, -0.6 * PER_CENT),
                ("descent", 0.1, 0, 0.1 * PER_CENT),
                ("descent", 2, -0.75 * PER_CENT, 0),
                ("descent", 9, -1 * PER_CENT, -0.25 * PER_CENT),
            ),
        )
        def test_equilibrium_supersaturation(
            variables, mask_label, dry_radius_um, min_value, max_value
        ):
            mask = np.logical_and(
                variables["masks"][mask_label], variables["height_above_cloud_base"] > 0
            )
            assert (variables["SS_eq"][dry_radius_um][mask] > min_value).all()
            assert (variables["SS_eq"][dry_radius_um][mask] < max_value).all()

        @staticmethod
        @pytest.mark.parametrize(
            "mask_label, dry_radius_um, min_value, max_value",
            (
                ("ascent", 0.1, 0, 0.5 * PER_CENT),
                ("ascent", 2, 0, 1 * PER_CENT),
                ("ascent", 9, 0.75 * PER_CENT, 2.5 * PER_CENT),
                ("descent", 0.1, -0.2 * PER_CENT, 0.1 * PER_CENT),
                ("descent", 2, -0.5 * PER_CENT, 0.25 * PER_CENT),
                ("descent", 9, 0.3 * PER_CENT, 0.8 * PER_CENT),
            ),
        )
        def test_effective_supersaturation(
            variables, mask_label, dry_radius_um, min_value, max_value
        ):
            mask = np.logical_and(
                variables["masks"][mask_label], variables["height_above_cloud_base"] > 0
            )
            assert (variables["SS_ef"][dry_radius_um][mask] > min_value).all()
            assert (variables["SS_ef"][dry_radius_um][mask] < max_value).all()
