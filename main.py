from __future__ import annotations

from pathlib import Path
from typing import (
    Union,
    TYPE_CHECKING
)

from elytra_component.honeybee.radiance.results import (
    read_annual_metrics,
    read_annual_raw,
    read_pit_results,
)
from elytra_component.honeybee.radiance.sources import (
    climatebased_sky,
    wea_from_epw,
)
from elytra_component.honeybee.radiance.simulation import (
    recipe_settings,
    run_annual,
    run_pit_grid,
)

if TYPE_CHECKING:
    from os import PathLike
    from elytra_component.honeybee.radiance.typing import AnnualResult


def main(
    hbjson_file: Union[str, "PathLike[str]"],
    epw_file: Union[str, "PathLike[str]"],
    wea_file: Union[str, "PathLike[str]"],
    cpu_count: int = 1,
) -> None:

    output_root = Path("outputs") / "honeybee" / "radiance"
    wea = wea_from_epw(epw_file)
    pit_sky = climatebased_sky(
        wea,
        3,
        21,
        9.0,
    )
    wea.write(output_root / "weather" / "weather.wea")

    print("Run annual daylight simulation")
    annual_result: "AnnualResult" = run_annual(
        hbjson_file,
        wea_file,
        settings=recipe_settings(
            folder=output_root / "annual_daylight",
            reload_old=True,
        ),
        silent=True,
    )

    print("annual project:", annual_result["project_folder"])
    print("annual simulation:", annual_result["simulation_folder"])
    print("annual results:", annual_result["results"])
    print("annual metrics:", annual_result["metrics"])
    print("annual aperture groups:", sorted(annual_result["aperture_groups"]))

    annual_raw = read_annual_raw(annual_result)
    official_metrics = read_annual_metrics(annual_result)
    first_group_id = sorted(annual_raw)[0]

    print("read annual raw results")
    print("first aperture group:", first_group_id)
    for grid_id, values in annual_raw[first_group_id]["total"].items():
        print("total", grid_id, values.shape)
    for grid_id, values in annual_raw[first_group_id]["direct"].items():
        print("direct", grid_id, values.shape)

    print("read official annual metrics")
    for metric_name, grid_values in official_metrics.items():
        for grid_id, values in grid_values.items():
            print(
                metric_name,
                grid_id,
                values.shape,
                float(values.min()),
                float(values.max()),
            )

    print("Run point-in-time grid simulation")
    pit_result = run_pit_grid(
        hbjson_file,
        pit_sky,
        settings=recipe_settings(
            folder=output_root / "point_in_time_grid",
            reload_old=True,
        ),
        silent=True,
    )

    print("pit project:", pit_result["project_folder"])
    print("pit simulation:", pit_result["simulation_folder"])
    print("pit results:", pit_result["results"])
    print("pit result files:", sorted(pit_result["result_files"]))

    pit_values = read_pit_results(pit_result)
    print("read point-in-time results")
    for grid_id, values in pit_values.items():
        print(grid_id, values.shape, float(values.min()), float(values.max()))


if __name__ == "__main__":
    main()
