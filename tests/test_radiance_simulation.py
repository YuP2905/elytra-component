from __future__ import annotations

from pathlib import Path

import pytest

from elytra_component.honeybee.radiance import (
    annual_metrics,
    certain_illuminance,
    read_annual_metrics,
    read_annual_raw,
    read_res_folder,
    read_pit_results,
    recipe_settings,
    run_annual,
    run_pit_grid,
    wea_from_epw,
)


def test_wea_can_be_created_from_example_epw(
    example_epw: Path,
) -> None:
    wea = wea_from_epw(example_epw)

    assert len(wea.direct_normal_irradiance.values) == 8760
    assert len(wea.diffuse_horizontal_irradiance.values) == 8760


@pytest.mark.engine
@pytest.mark.slow
def test_pit_grid_simulation_runs_and_reads_results(
    tmp_path: Path,
    example_hbjson: Path,
    require_radiance: None,
) -> None:
    result = run_pit_grid(
        example_hbjson,
        certain_illuminance(),
        recipe_settings(
            folder=tmp_path / "radiance",
            workers=2,
        ),
        silent=True,
    )

    assert result["simulation_folder"].is_dir()
    assert result["results"][0].is_dir()
    assert result["grids_info"][0].is_file()
    assert result["result_files"]["test_grid"].is_file()

    values = read_pit_results(result)
    folder_values = read_res_folder(result["results"][0])

    assert tuple(values) == ("test_grid",)
    assert tuple(folder_values) == ("test_grid",)
    assert values["test_grid"].shape == (1,)
    assert folder_values["test_grid"].shape == (1,)
    assert float(values["test_grid"][0]) > 0.0


@pytest.mark.engine
@pytest.mark.slow
def test_annual_daylight_simulation_reads_raw_and_metrics(
    tmp_path: Path,
    example_hbjson: Path,
    example_epw: Path,
    require_radiance: None,
) -> None:
    wea = wea_from_epw(example_epw)
    result = run_annual(
        example_hbjson,
        wea,
        settings=recipe_settings(
            folder=tmp_path / "annual",
            workers=2,
        ),
        silent=True,
    )

    raw_results = read_annual_raw(result)
    official_metrics = read_annual_metrics(result)
    custom_metrics = annual_metrics(
        result,
        "Always On",
    )

    group_id = "__static_apertures__/default"
    assert group_id in raw_results
    assert group_id in custom_metrics

    total_values = raw_results[group_id]["total"]["test_grid"]
    direct_values = raw_results[group_id]["direct"]["test_grid"]
    assert total_values.shape[0] == 1
    assert direct_values.shape[0] == 1
    assert total_values.shape == direct_values.shape
    assert total_values.shape[1] > 0

    assert set(official_metrics) == {
        "da",
        "cda",
        "udi",
        "udi_lower",
        "udi_upper",
    }

    grid_metrics = custom_metrics[group_id]["test_grid"]
    assert 0.0 <= grid_metrics["da"][0] <= 1.0
    assert 0.0 <= grid_metrics["cda"][0] <= 1.0
    assert 0.0 <= grid_metrics["udi"][0] <= 1.0
    assert grid_metrics["ase_hours"][0] >= 0.0
