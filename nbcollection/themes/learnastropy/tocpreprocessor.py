"""nbconvert preprocessor that extracts the document outline (TOC)."""

from __future__ import annotations

from collections.abc import Collection, Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from nbconvert.filters import add_anchor
from nbconvert.preprocessors import Preprocessor

if TYPE_CHECKING:
    from nbformat import NotebookNode


class TocPreprocessor(Preprocessor):
    """An nbconvert preprocessor that extracts the document outline (TOC).

    The TOC is available under the key `learn_astropy_toc` in the resources
    dictionary. It is a list of dictionaries, each of which represents a
    section in the document. Each dictionary has the following keys:

    - `title`: The plain text title of the section.
    - `children`: A list of dictionaries representing the children of the
      section.
    - `href`: The href of the section. E.g. ``#Section-title``.
    - `level`: The heading level of the section.
    """

    def preprocess(
        self, nb: NotebookNode, resources: dict[str, Any]
    ) -> tuple[NotebookNode, dict[str, Any]]:
        """Extract the document outline into the resources for the HTML exporter."""
        markdown = self._extract_markdown(nb)
        md = MarkdownIt()
        md_tokens = md.parse(markdown)
        token_tree = SyntaxTreeNode(md_tokens)
        sections = SectionChildren([])
        heading_nodes = [n for n in token_tree.children if n.type == "heading"]
        for node in heading_nodes:
            section = Section.create_from_node(node)
            sections.insert_section(section)

        # Add the document outine, including only the sections, but not
        # the h1 title
        resources["learn_astropy_toc"] = sections[0].children.export()

        return nb, resources

    def _extract_markdown(self, nb: NotebookNode) -> str:
        """Extract the markdown content from the notebook."""
        markdown_cells = [c.source for c in nb.cells if c.cell_type == "markdown"]
        return "\n\n".join(markdown_cells)


class SectionChildren(Collection):
    """A collection of Section objects."""

    def __init__(self, sections: list[Section]) -> None:
        self._sections = sections

    def __contains__(self, x: object) -> bool:
        return x in self._sections

    def __iter__(self) -> Iterator[Section]:
        return iter(self._sections)

    def __len__(self) -> int:
        return len(self._sections)

    def __getitem__(self, index: int) -> Section:
        return self._sections[index]

    def __repr__(self) -> str:
        return f"SectionChildren({self._sections})"

    def insert_section(self, section: Section) -> None:
        """Insert a section at the correct level of hierarchy."""
        if len(self) == 0:
            # No children, so append
            self._sections.append(section)
        elif self._sections[-1].level == section.level:
            # Same level as direct children, so append
            self._sections.append(section)
        else:
            # Not the same level as direct children, so insert into last child
            self._sections[-1].children.insert_section(section)

    def export(self) -> list[dict]:
        """Export the section hierarchy as a list of dictionaries."""
        return [s.as_dict() for s in self._sections]


@dataclass
class Section:
    """A section in the document and its children."""

    title: str
    """The plain text title of the section."""

    children: SectionChildren
    """The children of the section."""

    href: str = "#"
    """The href of the section."""

    level: int = 0
    """The heading level of the section."""

    @classmethod
    def create_from_node(cls, node: SyntaxTreeNode) -> Section:
        """Create a section from a Markdown heading node."""
        # The content of the heading can contain inline formatting. This is
        # a basic way to strip out code, bold, and italics. We need to
        # revisit this to strip out links.
        title = node.children[0].content
        title = title.replace("`", "")
        title = title.replace("*", "")
        title = title.replace("_", "")

        level = int(node.tag.lstrip("h"))

        # Use nbconvert's own add_anchor function to compute the anchor
        # href. Unfortunately this relies on a roundtrip through HTML. The
        # function that works directly on the title text isn't a pubilc API.
        header_html = f"<h{level}>{title}</h{level}>"
        header_html = add_anchor(header_html, anchor_link_text="#")
        header_soup = BeautifulSoup(header_html, "html.parser")
        try:
            href = header_soup.find("a")["href"]
        except KeyError:
            href = "#"

        return cls(title=title, children=SectionChildren([]), href=href, level=level)

    def as_dict(self) -> dict[str, Any]:
        """Convert the section to a dictionary."""
        return {
            "title": self.title,
            "children": [c.as_dict() for c in self.children],
            "href": self.href,
            "level": self.level,
        }
