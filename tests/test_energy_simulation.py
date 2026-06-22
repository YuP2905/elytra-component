from __future__ import annotations

from pathlib import Path

import pytest

from elytra_component.honeybee.energy import (
    load_eui,
    load_result_dictionary,
    run_energy_simulation,
    simulation_parameter,
    write_hbjson_2_osm,
)


@pytest.mark.engine
@pytest.mark.slow
def test_energy_simulation_writes_runs_and_reads_outputs(
    tmp_path: Path,
    example_hbjson: Path,
    example_epw: Path,
    require_openstudio: None,
) -> None:
    simulation_files = write_hbjson_2_osm(
        example_hbjson,
        example_epw,
        tmp_path / "energy",
        simulation_parameter(timestep=1),
    )

    assert simulation_files["osm"].is_file()
    assert simulation_files["idf"] is not None
    assert simulation_files["idf"].is_file()

    result = run_energy_simulation(
        simulation_files,
        example_epw,
        silent=True,
    )

    assert result["sql"].is_file()
    assert result["rdd"] is not None
    assert result["rdd"].is_file()

    eui = load_eui(result["sql"])
    output_names = load_result_dictionary(result["rdd"])

    assert eui["total_floor_area"] > 0.0
    assert eui["eui"] >= 0.0
    assert len(output_names) > 0
