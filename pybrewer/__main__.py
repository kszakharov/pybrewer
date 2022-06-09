from argparse import ArgumentParser, Namespace
from pathlib import Path

from pybrewer.formula import FileFormula, PoetryProjectFormula


def parse_args() -> Namespace:
    """Parses the command line arguments."""

    parser = ArgumentParser(description="Tool for management homebrew formulas.")
    subparsers = parser.add_subparsers()

    create = subparsers.add_parser("create", help="create a new formula")
    create.add_argument("project", default=Path(__file__).parent, help="path to project", type=Path)
    create.add_argument("formula", help="path to formula file", type=Path, nargs="?")
    create.set_defaults(func=formula_create)

    update = subparsers.add_parser("update", help="update an existing formula")
    update.add_argument("project", default=Path(__file__).parent, help="path to project", type=Path)
    update.add_argument("formula", help="path to formula file", type=Path)
    update.add_argument("--diff", help="show diff", action="store_true")
    update.set_defaults(func=formula_update)

    return parser.parse_args()


def formula_create(args: Namespace) -> None:
    formula = PoetryProjectFormula(args.project)
    if args.formula:
        formula.write(path=args.formula)
    else:
        formula.display()


def formula_update(args: Namespace) -> None:
    file_formula = FileFormula(args.formula)
    poetry_project_formula = PoetryProjectFormula(args.project)
    file_formula.update(poetry_project_formula)

    if args.diff:
        file_formula.diff()
    else:
        file_formula.write()


def main() -> None:
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
