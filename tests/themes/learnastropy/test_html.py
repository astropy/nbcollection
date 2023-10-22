"""Test for the Learn Astropy HTML theme."""

# mypy: disable-error-code="unreachable"

from __future__ import annotations

from pathlib import Path
from pprint import pprint
from typing import Any, cast

import pytest
from traitlets.config import Config

from nbcollection.themes.learnastropy.html import LearnAstropyHtmlExporter
from tests.support.themes import write_conversion


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_html_export(theme: str) -> None:
    """Integration test for the HTML export with the "color-excess" sample tutorial.

    Output is written to `_build/learnastropy/color-excess/{light|dark}`.
    """
    test_notebook = Path(__file__).parent.parent.joinpath("data/color-excess.ipynb")
    assert test_notebook.is_file()

    resources = {
        "learn_astropy_editor_url": (
            "https://mybinder.org/v2/gh/astropy/astropy-tutorials/"
            "main?labpath=tutorials%2Fcolor-excess%2Fcolor-excess.ipynb"
        ),
        "learn_astropy_source_url": (
            "https://github.com/astropy/astropy-tutorials/blob/main/tutorials/"
            "color-excess/color-excess.ipynb"
        ),
        "learn_astropy_ipynb_download_url": (
            "https://learn.astropy.org/tutorials/color-excess.ipynb"
        ),
    }

    config = Config()

    exporter = LearnAstropyHtmlExporter(config=config)
    exporter.theme = theme
    html, resources = exporter.from_filename(
        str(test_notebook.resolve()), resources=resources
    )

    assert "learn_astropy_toc" in resources
    toc = resources["learn_astropy_toc"]
    pprint(toc)
    # mypy insists that `toc` is a `str` here, but it's actually a
    # `list[dict[str, Any]]`. Doing a cast doesn't work?
    toc = cast(list[dict[str, Any]], toc)  # type: ignore[assignment]
    assert isinstance(toc, list)  # type: ignore[unreachable]
    assert toc[0]["title"] == "Authors"
    assert toc[0]["href"] == "#Authors"
    assert toc[1]["title"] == "Learning Goals"
    assert toc[1]["href"] == "#Learning-Goals"
    assert toc[2]["title"] == "Keywords"
    assert toc[2]["href"] == "#Keywords"
    assert toc[3]["title"] == "Companion Content"
    assert toc[3]["href"] == "#Companion-Content"
    assert toc[4]["title"] == "Summary"
    assert toc[4]["href"] == "#Summary"
    assert toc[5]["title"] == "Introduction"
    assert toc[5]["href"] == "#Introduction"
    assert toc[6]["title"] == "Examples"
    assert toc[6]["href"] == "#Examples"
    assert toc[6]["children"][0]["title"] == "Investigate Extinction Models"
    assert toc[6]["children"][0]["href"] == "#Investigate-Extinction-Models"
    assert toc[6]["children"][1]["title"] == "Deredden a Spectrum"
    assert toc[6]["children"][1]["href"] == "#Deredden-a-Spectrum"
    assert toc[6]["children"][2]["title"] == "Calculate Color Excess with synphot"
    assert toc[6]["children"][2]["href"] == "#Calculate-Color-Excess-with-synphot"
    assert toc[7]["title"] == "Exercise"
    assert toc[7]["href"] == "#Exercise"

    write_conversion(
        base_dir=f"learnastropy/color-excess/{theme}", content=html, resources=resources
    )
