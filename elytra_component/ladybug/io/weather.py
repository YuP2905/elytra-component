from __future__ import annotations
from pathlib import Path
from typing import (
    Optional,
    Union,
    cast,
    TYPE_CHECKING,
)
from urllib.parse import unquote, urlparse
from urllib.request import urlretrieve
import webbrowser

from ladybug.config import folders
from ladybug.epw import EPW
from ladybug.futil import unzip_file
from ladybug.stat import STAT

from ..config import LADYBUG_CONFIG

if TYPE_CHECKING:
    from os import PathLike

    from ..typing import WeatherFilePaths


def open_epw_map(
    is_open: bool = False,
    epw_map_url: Optional[str] = None,
) -> None:
    """
    Oepn the EPW map in a web browser.
    Args:
        is_open: Whether to open the EPW map in a web browser.
        epw_map_url: The URL of the EPW map to open. If None, the default EPW map URL will be used.
    Returns:
        None
    """
    map_url = epw_map_url or LADYBUG_CONFIG.DEFAULT_EPW_MAP_URL
    if is_open:
        webbrowser.open(
            map_url,
            new=2,
            autoraise=True,
        )


def download_weathers(
    weather_url: str,
    folder: Optional[Union["PathLike[str]", str]] = None,
) -> "WeatherFilePaths":
    """
    Automatically download a .zip file from a URL where climate data resides,
    unzip the file, and open .epw, .stat, and ddy weather files.
        Args:
            weather_URL: Text representing the URL at which the climate data resides.
                To open the a map interface for all publicly availabe climate data,
                use the "LB EPWmap" component.
            folder: An optional file path to a directory into which the weather file
                will be downloaded and unziped.  If None, the weather files will be
                downloaded to the ladybug default weather data folder and placed in
                a sub-folder with the name of the weather file location.

        Returns:
            epw_file: The file path of the downloaded epw file.
            stat_file: The file path of the downloaded stat file.
            ddy_file: The file path of the downloaded ddy file.
    """
    weather_url = weather_url.strip()
    if not weather_url:
        raise ValueError(
            "The weather URL cannot be empty."
        )

    parsed_url = urlparse(weather_url)
    url_path = unquote(parsed_url.path)

    # Region \ Country \ State/Province/Prefecture \ xxx.epw or xxx.zip or all
    url_path = Path(url_path)

    # |  url   | suffix |  name   | stem |
    # | :----: | :----: | :-----: | :--: |
    # | xx.epw |  .epw  | xxx.epw | xxx  |
    # | xx.zip |  .zip  | xxx.zip | xxx  |
    # |  /all  |        |   all   | all  |
    weather_suffix = url_path.suffix.lower()
    weather_stem = url_path.stem
    download_file_name = url_path.name

    is_lone_epw = weather_suffix == ".epw"
    is_all_url = weather_stem.lower() == "all" and not weather_suffix

    if is_all_url:
        # State or Province or Prefecture Name
        weather_name = url_path.parent.name
        weather_stem = weather_name

        # State or Province or Prefecture.zip
        download_file_name = f"{weather_name}.zip"

        repl_section = f"{weather_name}/all"
        new_sction = f"{weather_name}/{weather_name}.zip"

        weather_url = weather_url.replace(
            repl_section,
            new_sction,
        )
        weather_url = weather_url.replace(
            "www.energyplus.net/weather-download",
            "energyplus-weather.s3.amazonaws.com",
        )
        weather_url = weather_url.replace(
            "energyplus.net/weather-download",
            "energyplus-weather.s3.amazonaws.com",
        )

        https_len = len("https://")
        weather_url = (
            weather_url[:https_len]
            + weather_url[https_len:].replace("//", "/")
        )
    elif weather_suffix not in {".epw", ".zip"}:
        raise ValueError(
            "The weather URL must end with .epw, .zip, or /all."
        )

    folder_path = Path(cast(str, folders.default_epw_folder)) if folder is None else Path(folder)
    folder_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    weather_folder = folder_path / weather_stem
    weather_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    epw_file = weather_folder / f"{weather_stem}.epw"
    stat_file = weather_folder / f"{weather_stem}.stat"
    ddy_file = weather_folder / f"{weather_stem}.ddy"

    if is_lone_epw:
        if not epw_file.is_file():
            urlretrieve(
                weather_url,
                str(epw_file),
            )
        return epw_file, None, None

    if not epw_file.is_file():
        zip_file_path = (
            folder_path / download_file_name
            if is_all_url
            else weather_folder / download_file_name
        )

        if not zip_file_path.is_file():
            urlretrieve(
                weather_url,
                str(zip_file_path),
            )

        unzip_file(
            str(zip_file_path),
            str(weather_folder),
        )

    return (
        epw_file,
        stat_file if stat_file.is_file() else None,
        ddy_file if ddy_file.is_file() else None,
    )


def weather_to_ddy(
    weather_file: Union["PathLike[str]", str],
    percentile: float = 0.4,
    monthly_cool: bool = False,
    folder: Optional[Union["PathLike[str]", str]] = None,
) -> Path:
    """Create a DDY file from an EPW or STAT weather file."""
    weather_path = Path(weather_file)
    if not weather_path.is_file():
        raise FileNotFoundError(
            f"The weather file was not found: {weather_path}"
        )
    if not 0.0 <= percentile <= 50.0:
        raise ValueError(
            f"The percentile must be between 0 and 50: {percentile}"
        )

    weather_suffix = weather_path.suffix.lower()
    is_epw = weather_suffix == ".epw"
    if weather_suffix not in {".epw", ".stat"}:
        raise ValueError(
            f"The weather file must end with .epw or .stat: {weather_path}"
        )

    folder_path = (
        Path(cast(str, folders.default_epw_folder)) / "ddy"
        if folder is None
        else Path(folder)
    )
    folder_path.mkdir(
        parents=True,
        exist_ok=True,
    )
    ddy_file_path = folder_path / f"{weather_path.stem}.ddy"

    if is_epw:
        epw = EPW(str(weather_path))
        ddy_file = (
            epw.to_ddy_monthly_cooling(
                str(ddy_file_path),
                percentile,
                2,
            )
            if monthly_cool
            else epw.to_ddy(
                str(ddy_file_path),
                percentile,
            )
        )
        return Path(ddy_file)

    stat = STAT(str(weather_path))
    ddy_file = (
        stat.to_ddy_monthly_cooling(
            str(ddy_file_path),
            percentile,
            2,
        )
        if monthly_cool
        else stat.to_ddy(
            str(ddy_file_path),
            percentile,
        )
    )
    return Path(cast(str, ddy_file))
