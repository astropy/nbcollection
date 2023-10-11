"""HTML Exporter for Learn Astropy Tutorials."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from nbconvert.exporters.html import HTMLExporter
from traitlets.config import Config

from .tocpreprocessor import TocPreprocessor


class LearnAstropyHtmlExporter(HTMLExporter):
    """HTML exporter for Learn Astropy HTML notebooks."""

    export_from_notebook = "Learn Astropy HTML"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Require the TocPreprocessor to populate the table of contents
        # in the resources
        if "config" not in kwargs:
            kwargs["config"] = Config()
        kwargs["config"].HTMLExporter.preprocessors = [TocPreprocessor]

        super().__init__(*args, **kwargs)

        # Add the default template to the search path
        self.extra_template_basedirs.append(self._template_name_default())

    def _template_name_default(self) -> str:
        """Select built-in HTML theme as the default.

        Overrides `HTMLExporter._template_name_default`.
        """
        return str(Path(__file__).parent.joinpath("templates").joinpath("html"))

    def _init_resources(self, resources: dict[str, Any]) -> dict[str, Any]:
        """Add additional metadata to the Jinja context via the resources dictionary."""
        # This is an exporter hook that we can use in the future to add
        # additional metadata to the Jinja context.
        return super()._init_resources(resources)
