import requests
from poetry.packages import DependencyPackage


class Package:
    """Base class for all packages."""

    __registry__ = {}

    @classmethod
    def create(cls, package: DependencyPackage):
        return cls.__registry__[package.source_type](package)

    def __init_subclass__(cls) -> None:
        cls.__registry__[cls.__source_type__] = cls

    def __lt__(self, other) -> bool:
        return self.name < other.name

    def __eq__(self, other) -> bool:
        return self.tarball_url == other.tarball_url

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: name={self.name}>"


class PyPIPackage(Package):
    """Package from Python Package Index (PyPI)."""

    __source_type__ = None

    def __init__(self, package: DependencyPackage) -> None:
        self.package = package
        self.name = package.name
        self.version = str(package.version)

        self.url = f"https://pypi.org/pypi/{self.name}/{self.version}/json"
        self.info = requests.get(self.url).json()

        self.release = self.info["urls"][-1]
        self.sha256 = self.release["digests"]["sha256"]
        self.tarball_url = self.release["url"]


class GitPackage(Package):
    """Package from Git repository.

    Currently only GitHub repos are supported.
    """

    __source_type__ = "git"

    def __init__(self, package: DependencyPackage) -> None:
        self.package = package
        self.name = package.name
        #self.version = str(package.version)
        self.branch = package.source_reference
        # https://docs.github.com/en/rest/reference/repos#download-a-repository-archive-tar
        self.url = package.source_url.removesuffix(".git")
        self.tarball_url = f"{self.url}/tarball/{self.branch}"


class FormulaPackage(Package):
    """Package from Formula file."""

    __source_type__ = "formula"

    def __init__(self, package: dict[str, str]) -> None:
        self.name = package["resource"]
        self.tarball_url = package["url"]
        if "sha256" in package:
            self.sha256 = package["sha256"]
