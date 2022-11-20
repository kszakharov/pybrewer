from __future__ import annotations

import re
import textwrap
from datetime import datetime
from difflib import unified_diff
from pathlib import Path, PosixPath
from typing import Optional

from jinja2 import Template
from poetry.factory import Factory
from poetry.core.packages.dependency_group import MAIN_GROUP
from pydantic import BaseModel
from ttp import ttp

from pybrewer.package import FormulaPackage, Package

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from poetry.core.packages.dependency import Dependency
    from poetry.repositories import Repository
    from poetry.core.packages.package import Package
    from poetry.poetry import Poetry

TEMPLATES_DIR = Path(__file__).parent / "templates"
JINJA2_TEMPLATE = TEMPLATES_DIR / "formula.rb.j2"
TTP_TEMPLATE = TEMPLATES_DIR / "formula.txt"


class Completion(BaseModel):
    """Shell completion model."""

    shell: str
    path: str


class Formula(BaseModel):

    name: str
    description: str
    homepage: str
    head: Optional[str]
    revision: Optional[int] = None
    completions: list[Completion] = []

    python_version: str
    resources: list[Package] = []

    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def render(self) -> str:
        """Render formula as text."""

        template = Template(JINJA2_TEMPLATE.read_text())
        text = template.render(formula=self)
        # Lines containing only spaces are converted to one newline character
        text = textwrap.dedent(text)
        # Use one blank line as block separator
        text = re.sub(r"\n{3,}", r"\n\n", text)

        return text

    def display(self) -> None:
        """Display formula as text."""

        print(self.render())

    def write(self, path: PosixPath) -> None:
        path.write_text(self.render() + "\n")

    def update(self, other: Formula) -> None:
        self.description = other.description
        self.homepage = other.homepage
        self.head = other.head
        self.completions = other.completions

        if self.resources != other.resources:
            self.resources = other.resources
            if self.revision:
                self.revision += 1
            else:
                self.revision = 1

class PoetryProjectFormula(Formula):
    """Formula for a Poetry project."""

    def __init__(self, path: Path) -> None:

        poetry = Factory().create_poetry(Path(path).expanduser())
        content = poetry.file.read()
        #homebrew = content["tool"]["poetry"] | content["tool"].get("pybrewer", {})
        poetry_config = content["tool"]["poetry"]
        pybrewer_config = content["tool"].get("pybrewer", {})
        config = poetry_config | pybrewer_config

        head_string = ""
        if "head" in pybrewer_config.get("git", {}):
            head_string = f'"{pybrewer_config["git"]["head"]}"'
            if pybrewer_config["git"]["head"].startswith("git@"):
                head_string += ", :using => :git"
            if "branch" in pybrewer_config["git"]:
                head_string += f', branch: "{pybrewer_config["git"]["branch"]}"'

        completions = [
            Completion(shell=shell, path=path)
            for shell, path in pybrewer_config.get("completions", {}).items()
        ]

        exclude = pybrewer_config.get("dependencies", {}).get("exclude", [])

        def get_dependencies(dependencies: list[Dependency], locked_repository: Repository) -> list[Package]:
            all_packages = []
            for dependency in dependencies:
                packages = locked_repository.find_packages(dependency=dependency)
                for package in packages:
                    all_packages += get_dependencies(
                        dependencies=package.requires,
                        locked_repository=locked_repository,
                    )
                    all_packages.append(package)
            return all_packages

        locked_repository = poetry.locker.locked_repository()

        dg = poetry.package.dependency_group(MAIN_GROUP)
        dependencies = get_dependencies(
            dependencies=dg.dependencies,
            locked_repository=locked_repository,
        )
        dependencies = {(dep.name, dep.version): dep for dep in dependencies}
        dependencies = dependencies.values()

        super().__init__(
            name=poetry_config["name"][:1].upper() + poetry_config["name"][1:],
            description=poetry_config.get("description"),
            homepage=poetry_config.get("homepage"),
            head=head_string,
            completions=completions,

            repository_url=poetry_config.get("repository"),
            documentation_url=poetry_config.get("documentation"),

            python_version=poetry.package.python_versions[1:],
            resources=sorted(
                [
                    Package.create(package)
                    for package in dependencies
                    if package.name not in exclude
                ]
            ),
        )


class FileFormula(Formula):
    """Formula for a file."""

    formula_path: PosixPath
    formula_string: str

    def __init__(self, formula_path: PosixPath) -> None:
        formula_string = formula_path.read_text()
        parser = ttp(formula_string, template=TTP_TEMPLATE.read_text())
        parser.parse()
        result = parser.result(structure="flat_list")[0]

        head_string = f'"{result["head"]}"'
        if result["head"].startswith("git@"):
            head_string += ", :using => :git"
        if result["branch"]:
            head_string += f', branch: "{result["branch"]}"'

        super().__init__(
            name=result["name"],
            description=result["description"],
            homepage=result["homepage"],
            head=head_string,
            revision=result["revision"],
            completions=result.get("completions", []),

            repository_url="",
            documentation_url="",

            python_version=result["python_version"],
            resources=[FormulaPackage(resouce) for resouce in result["resources"]],
            formula_string=formula_string,
            formula_path=formula_path,
        )

    def diff(self) -> None:
        """Diff formula with file."""

        changes = list(
            unified_diff(
                self.formula_string.splitlines(),
                self.render().splitlines(),
                fromfile=str(self.formula_path),
                tofile=str(self.formula_path),
                fromfiledate=datetime.fromtimestamp(
                    self.formula_path.stat().st_mtime
                ).isoformat(sep=" ", timespec="seconds"),
                tofiledate=datetime.now().isoformat(sep=" ", timespec="seconds"),
                lineterm="",
            )
        )

        if changes:
            for line in changes:
                if line.startswith("+"):
                    print("\33[32m" + line + "\033[0m")
                elif line.startswith("-"):
                    print("\33[31m" + line + "\033[0m")
                else:
                    print(line)
        else:
            print("\33[32m" + "No changes." + "\033[0m")

    def write(self) -> None:
        super().write(path=self.formula_path)
