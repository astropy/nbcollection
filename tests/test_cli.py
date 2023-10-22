import os
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from nbcollection.__main__ import main


@pytest.mark.parametrize("command", ["execute", "convert"])
def test_default(tmp_path, command):
    test_root_path = os.path.dirname(__file__)

    nb_name = "notebook1.ipynb"
    nb_path = os.path.join(test_root_path, f"data/nb_test1/{nb_name}")
    nb_root_path = os.path.split(nb_path)[0]
    counter = 0

    # Default behavior, one notebook input, no specified build path
    _ = main(["nbcollection", command, nb_path])
    assert "_build" in os.listdir(nb_root_path)
    assert nb_name in os.listdir(os.path.join(nb_root_path, "_build"))

    # Default behavior, one notebook input, specified build path
    build_path = tmp_path / f"test_{command}_{counter}"
    counter += 1
    build_path.mkdir()
    _ = main(["nbcollection", command, nb_path, f"--build-path={build_path!s}"])
    assert "_build" in os.listdir(str(build_path))
    assert nb_name in os.listdir(os.path.join(build_path, "_build"))

    # Default behavior, one notebook path, no specified build path
    _ = main(["nbcollection", command, nb_root_path])
    assert "_build" in os.listdir(os.path.join(nb_root_path, ".."))
    assert nb_name in os.listdir(os.path.join(nb_root_path, "../_build/nb_test1"))

    # Default behavior, one notebook path, specified build path
    build_path = tmp_path / f"test_{command}_{counter}"
    counter += 1
    build_path.mkdir()
    _ = main(["nbcollection", command, nb_root_path, f"--build-path={build_path!s}"])
    assert "_build" in os.listdir(str(build_path))
    assert nb_name in os.listdir(os.path.join(build_path, "_build/nb_test1"))

    # Two notebook files, specified build path
    nb_path1 = os.path.join(test_root_path, "data/nb_test1/notebook1.ipynb")
    nb_path2 = os.path.join(test_root_path, "data/nb_test2/notebook2.ipynb")
    build_path = tmp_path / f"test_{command}_{counter}"
    counter += 1
    build_path.mkdir()
    _ = main(
        ["nbcollection", command, f"--build-path={build_path!s}", nb_path1, nb_path2]
    )
    assert "_build" in os.listdir(str(build_path))
    for nb_name in ["notebook1.ipynb", "notebook2.ipynb"]:
        assert nb_name in os.listdir(os.path.join(build_path, "_build"))


@pytest.mark.parametrize("command", ["execute", "convert"])
def test_flatten(command):
    test_root_path = os.path.dirname(__file__)

    nb_root_path = os.path.join(test_root_path, "data/my_notebooks")

    # One notebook path, no specified build path, but flatten the file structure
    _ = main(["nbcollection", command, nb_root_path, "--flatten"])
    assert "_build" in os.listdir(os.path.join(nb_root_path, ".."))
    for nb_name in ["notebook1", "notebook2", "notebook3"]:
        assert f"{nb_name}.ipynb" in os.listdir(
            os.path.join(nb_root_path, "../_build/")
        )

        if command == "convert":
            assert f"{nb_name}.html" in os.listdir(
                os.path.join(nb_root_path, "../_build/")
            )


def test_index(tmp_path):
    test_root_path = os.path.dirname(__file__)

    nb_root_path = os.path.join(test_root_path, "data/my_notebooks")
    index_tpl_path = os.path.join(test_root_path, "data/default.tpl")

    # Make an index file with more complex notebook path structure
    build_path = tmp_path / "test_index"
    _ = main(
        [
            "nbcollection",
            "convert",
            nb_root_path,
            f"--build-path={build_path!s}",
            "--make-index",
            f"--index-template={index_tpl_path}",
        ]
    )
    assert "_build" in os.listdir(str(build_path))
    assert "index.html" in os.listdir(str(build_path / "_build"))

    # Flatten the build directory structure and make an index file
    _ = main(
        [
            "nbcollection",
            "convert",
            nb_root_path,
            "--flatten",
            "--make-index",
            f"--index-template={index_tpl_path}",
        ]
    )
    assert "_build" in os.listdir(os.path.join(nb_root_path, ".."))
    build_path = os.path.join(nb_root_path, "../_build/")
    assert "index.html" in os.listdir(build_path)


def test_learn_astropy_theme(tmp_path):
    """Build a site and verify that links are populated correctly."""
    source_root = Path(__file__).parent / "data" / "my_notebooks"
    build_path = tmp_path / "test_learn_astropy_theme"

    _ = main(
        [
            "nbcollection",
            "convert",
            str(source_root),
            f"--build-path={build_path!s}",
            "--flatten",
            "--github-url",
            "https://github.com/astropy/astropy-tutorials",
            "--github-path",
            "tutorials",
            "--github-branch",
            "main",
        ]
    )

    # Test links
    html_path = build_path / "_build" / "notebook1.html"
    soup = BeautifulSoup(html_path.read_text(), "html.parser")
    header_nav = soup.find("nav", class_="at-header-nav")
    binder_link = header_nav.find("a", string="Open in Binder")
    assert binder_link.attrs["href"] == (
        "https://mybinder.org/v2/gh/astropy/astropy-tutorials/main"
        "?labpath=tutorials%2Fnotebook1.ipynb"
    )
    github_link = header_nav.find("a", string="View on GitHub")
    assert github_link.attrs["href"] == (
        "https://github.com/astropy/astropy-tutorials/blob/main/tutorials/notebook1.ipynb"
    )
    download_link = header_nav.find("a", string="Download")
    assert download_link.attrs["href"] == "notebook1.ipynb"


# Too scary...
# def teardown_module():
#     for path in BUILD_PATHS:
#         if path is not None and os.path.exists(path):
