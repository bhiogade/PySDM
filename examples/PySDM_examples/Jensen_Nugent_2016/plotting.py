from matplotlib import pyplot
import numpy as np
from PySDM.physics import si, in_unit
from PySDM.physics.constants import PER_CENT


def figure(output, settings, simulation):
    cloud_base = 300 * si.m
    y_axis = np.asarray(output["products"]["z"]) - settings.z0 - cloud_base

    masks = {}
    masks["ascent"] = np.asarray(output["products"]["t"]) < settings.t_end_of_ascent
    masks["descent"] = masks["ascent"] == False

    colors = {"ascent": "r", "descent": "b"}

    fig, axs = pyplot.subplot_mosaic(
        mosaic=[["r", "S"]], width_ratios=[3, 1], sharey=True
    )

    for label, mask in masks.items():
        axs["S"].plot(
            in_unit(np.asarray(output["products"]["S_max"]), PER_CENT)[mask],
            y_axis[mask],
            label=label,
            color=colors[label],
        )
    axs["S"].set_xlim(-1, 1)
    axs["S"].set_xlabel("S (%)")
    axs["S"].legend()

    for drop_id in (
        18,
        29,
        70,
        89,
        -1,
    ):  # TODO: bug! why rightmost drop is not 500 nm ???
        for label, mask in masks.items():
            axs["r"].plot(
                in_unit(np.asarray(output["attributes"]["radius"][drop_id]), si.um)[
                    mask
                ],
                y_axis[mask],
                label=(
                    f"{in_unit(simulation.r_dry[drop_id], si.nm):.3g} nm"
                    if label == "ascent"
                    else ""
                ),
                color=colors[label],
            )
    axs["r"].legend()
    axs["r"].set_xlim(0, 15)
    axs["r"].set_xlabel("r$_c$ (µm)")
    axs["r"].set_ylabel("height above cloud base (m)")

    for ax in axs.values():
        ax.grid()