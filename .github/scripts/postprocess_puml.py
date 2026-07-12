"""Post-process a pyreverse-generated PlantUML class diagram.

Two things pyreverse won't do on its own:

1. Group classes into their packages. pyreverse emits a flat diagram where classes are
   wired directly to one another, with the package structure only encoded in the (unused)
   dotted aliases. Rewriting each alias from pkg.Module.Class to pkg.Class and enabling
   PlantUML namespaces nests every class inside a box for its package.

2. Draw class-less modules. SoundscapeVReapy.py is the entry point but declares no class,
   so it is analysed and then dropped. Modules with no class become <<module>> nodes
   carrying their globals and functions, with dependency arrows to the classes they import.

Usage: postprocess_puml.py DIAGRAM.puml [--ignore=a,b] TARGET [TARGET ...]
"""

import argparse
import ast
import pathlib
import re
import sys

CLASS_ALIAS_RE = re.compile(r'^class\s+"[^"]*"\s+as\s+(\S+)', re.MULTILINE)


def python_files(target: pathlib.Path, ignore: set[str]) -> list[pathlib.Path]:
    if target.is_file():
        return [target]
    return [
        path
        for path in sorted(target.rglob("*.py"))
        if not ignore & set(path.parts)
    ]


def module_name(path: pathlib.Path) -> str:
    parts = list(path.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def signature(func: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = [arg.arg for arg in func.args.args]
    return f"{func.name}({', '.join(args)})"


def globals_of(tree: ast.Module) -> list[str]:
    names = []
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else []
        if isinstance(node, ast.AnnAssign):
            targets = [node.target]
        names += [t.id for t in targets if isinstance(t, ast.Name)]
    return names


def imported_names(tree: ast.Module) -> dict[str, str]:
    """Map each imported name to the dotted path pyreverse would alias it as."""
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and not node.level:
            for alias in node.names:
                found[alias.name] = f"{node.module}.{alias.name}"
    return found


def module_node(name: str, tree: ast.Module, known_aliases: set[str]) -> str | None:
    functions = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if not functions:
        return None  # e.g. an empty __init__.py; nothing worth drawing

    lines = [f'class "{name.rsplit(".", 1)[-1]}" as {name} <<module>> {{']
    lines += [f"  {var}" for var in globals_of(tree)]
    lines += [f"  {signature(func)}" for func in functions]
    lines.append("}")

    edges = sorted(
        alias for alias in imported_names(tree).values() if alias in known_aliases
    )
    lines += [f"{name} ..> {edge}" for edge in edges]
    return "\n".join(lines)


def add_module_nodes(
    diagram: str, targets: list[pathlib.Path], ignore: set[str]
) -> str:
    known_aliases = set(CLASS_ALIAS_RE.findall(diagram))

    blocks = []
    for target in targets:
        for path in python_files(target, ignore):
            tree = ast.parse(path.read_text())
            if any(isinstance(node, ast.ClassDef) for node in tree.body):
                continue  # pyreverse already drew this one
            block = module_node(module_name(path), tree, known_aliases)
            if block:
                blocks.append(block)

    print(f"Added {len(blocks)} <<module>> node(s).")
    if not blocks:
        return diagram
    # The <<module>> nodes reference classes, so they must land before @enduml.
    return diagram.replace("@enduml", "\n".join(blocks) + "\n@enduml")


def group_into_packages(diagram: str) -> str:
    # pkg.Module.Class -> pkg.Class: the module level is noise once the classes are
    # boxed by package, and dropping it keeps one box per package rather than per file.
    renames = {}
    for alias in CLASS_ALIAS_RE.findall(diagram):
        parts = alias.split(".")
        if len(parts) > 1:
            renames[alias] = ".".join(parts[:-2] + parts[-1:])

    # Two same-named classes in one package would collide into a single node; keep the
    # module level for those rather than silently merging them.
    collisions = {
        new for new in renames.values() if list(renames.values()).count(new) > 1
    }
    renames = {old: new for old, new in renames.items() if new not in collisions}
    if collisions:
        print(f"Kept module level for colliding names: {', '.join(sorted(collisions))}")

    # Longest alias first, so a short alias can't rewrite part of a longer one.
    for old in sorted(renames, key=len, reverse=True):
        diagram = re.sub(
            rf"(?<![\w.]){re.escape(old)}(?![\w.])", renames[old], diagram
        )

    print(f"Grouped {len(renames)} class(es) into packages.")
    return diagram.replace("set namespaceSeparator none", "set namespaceSeparator .")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("diagram", type=pathlib.Path)
    parser.add_argument("targets", nargs="+", type=pathlib.Path)
    parser.add_argument("--ignore", default="")
    args = parser.parse_args()

    ignore = {part for part in args.ignore.split(",") if part}
    diagram = args.diagram.read_text()

    # Module nodes are added first, while aliases still carry the module level that
    # pyreverse and the import statements agree on.
    diagram = add_module_nodes(diagram, args.targets, ignore)
    diagram = group_into_packages(diagram)

    args.diagram.write_text(diagram)
    return 0


if __name__ == "__main__":
    sys.exit(main())
