#!/usr/bin/env python3
"""
py2md_docs.py

1) Recorre un árbol de Python y genera Markdown por módulo.
2) Actualiza automáticamente `mkdocs.yml` para incluir la referencia generada.

Uso:
  python tools/py2md_docs.py --src src --out docs/reference --mkdocs mkdocs.yml \
      --section "Referencia" --group "API" --include-comments
"""

from __future__ import annotations
import ast, io, os, tokenize
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
import argparse

# ---------- MODELOS ----------

@dataclass
class FunctionDoc:
    name: str
    qualname: str
    signature: str
    doc: str | None
    lineno: int

@dataclass
class ClassDoc:
    name: str
    qualname: str
    doc: str | None
    lineno: int
    methods: List[FunctionDoc] = field(default_factory=list)

@dataclass
class ModuleDoc:
    path: Path
    module_name: str
    package_path: str
    doc: str | None
    classes: List[ClassDoc] = field(default_factory=list)
    functions: List[FunctionDoc] = field(default_factory=list)
    comments: List[Tuple[int, str]] = field(default_factory=list)

# ---------- HELPERS ----------

def _expr_to_str(expr: ast.AST) -> str:
    try:
        return ast.unparse(expr)  # Python 3.9+
    except Exception:
        if isinstance(expr, ast.Constant):
            return repr(expr.value)
        if isinstance(expr, ast.Name):
            return expr.id
        return "..."

def _arg_to_str(arg: ast.arg, default: Optional[ast.AST]=None) -> str:
    s = arg.arg
    if default is not None:
        s += "=" + _expr_to_str(default)
    return s

def _format_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = node.args
    parts: List[str] = []
    # posicionales
    pos_defaults = [None] * (len(args.args) - len(args.defaults)) + list(args.defaults)
    for a, d in zip(args.args, pos_defaults):
        parts.append(_arg_to_str(a, d))
    # *args
    if args.vararg:
        parts.append("*" + args.vararg.arg)
    # kw-only
    if args.kwonlyargs and not args.vararg and not args.kwarg:
        parts.append("*")
    for a, d in zip(args.kwonlyargs, args.kw_defaults):
        parts.append(_arg_to_str(a, d))
    # **kwargs
    if args.kwarg:
        parts.append("**" + args.kwarg.arg)
    ann = f" -> {_expr_to_str(node.returns)}" if node.returns else ""
    return f"({', '.join(parts)}){ann}"

def _gather_comments(code: str) -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []
    buff = io.StringIO(code)
    for tok in tokenize.generate_tokens(buff.readline):
        if tok.type == tokenize.COMMENT:
            text = tok.string.lstrip("#").strip()
            if text:
                out.append((tok.start[0], text))
    return out

def _public(name: str) -> bool:
    return not name.startswith("_")

# ---------- PARSE ----------

def parse_module(py_path: Path, src_root: Path) -> ModuleDoc:
    code = py_path.read_text(encoding="utf-8")
    mod = ast.parse(code)
    module_doc = ast.get_docstring(mod)
    rel = py_path.relative_to(src_root)
    module_name = ".".join(rel.with_suffix("").parts)
    package_path = str(rel.as_posix())

    classes: List[ClassDoc] = []
    functions: List[FunctionDoc] = []

    for node in mod.body:
        if isinstance(node, ast.ClassDef) and _public(node.name):
            cdoc = ClassDoc(
                name=node.name,
                qualname=f"{module_name}.{node.name}",
                doc=ast.get_docstring(node),
                lineno=node.lineno,
                methods=[]
            )
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and _public(sub.name):
                    cdoc.methods.append(FunctionDoc(
                        name=sub.name,
                        qualname=f"{module_name}.{node.name}.{sub.name}",
                        signature=_format_signature(sub),
                        doc=ast.get_docstring(sub),
                        lineno=sub.lineno
                    ))
            classes.append(cdoc)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _public(node.name):
            functions.append(FunctionDoc(
                name=node.name,
                qualname=f"{module_name}.{node.name}",
                signature=_format_signature(node),
                doc=ast.get_docstring(node),
                lineno=node.lineno
            ))

    comments = _gather_comments(code)
    return ModuleDoc(
        path=py_path,
        module_name=module_name,
        package_path=package_path,
        doc=module_doc,
        classes=sorted(classes, key=lambda c: c.name.lower()),
        functions=sorted(functions, key=lambda f: f.name.lower()),
        comments=comments
    )

# ---------- GENERACIÓN MD ----------

def md_for_module(m: ModuleDoc, include_comments: bool = False) -> str:
    title = m.module_name or m.path.stem
    out: List[str] = []
    out.append(f"# `{title}`\n")
    out.append(f"*Source:* `{m.package_path}`\n")

    if m.doc:
        out.append("\n# Overview\n")
        out.append(m.doc.strip() + "\n")

    if m.classes:
        out.append("\n# Classes\n")
        for c in m.classes:
            out.append(f"###`{c.name}`\n")
            if c.doc:
                out.append(c.doc.strip() + "\n")
            if c.methods:
                out.append("\n#### Methods\n")
                for f in c.methods:
                    out.append(f"- **`{f.name}{f.signature}`**  \n")
                    if f.doc:
                        out.append(f"  {f.doc.strip()}\n")

    if m.functions:
        out.append("\n# Functions")
        for f in m.functions:
            # add the way to import 
            out.append(f"## `{f.name}{f.signature}`\n")

            out.append(f"```python\nfrom {f.qualname} import {f.name}\n```\n")

            if f.doc:
                out.append(f"{f.doc.strip()}\n")

    if include_comments and m.comments:
        out.append("\n## Comment index\n")
        for ln, txt in m.comments:
            out.append(f"- L{ln}: {txt}")

    out.append("\n---\n")
    out.append(f"*Auto-generated by `py2md_docs.py`.*\n")
    return "\n".join(out)

# ---------- MOTOR ----------

def generate_docs(src_dir: Path, out_dir: Path, include_comments: bool, mirror_tree: bool) -> List[Path]:
    src_dir = src_dir.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    md_paths: List[Path] = []

    for py in src_dir.rglob("*.py"):
        if any(part in {"__pycache__", "venv", ".venv", "build", "dist", "site"} for part in py.parts):
            continue
        mdoc = parse_module(py, src_dir)
        if mirror_tree:
            rel = py.relative_to(src_dir).with_suffix(".md")
            dst = (out_dir / rel)
        else:
            name = ".".join(py.relative_to(src_dir).with_suffix("").parts) + ".md"
            dst = out_dir / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(md_for_module(mdoc, include_comments=include_comments), encoding="utf-8")
        md_paths.append(dst)

    return md_paths

# ---------- MKDOCS.YML AUTO-UPDATE ----------

def update_mkdocs_yaml(mkdocs_path: Path, docs_root: Path, md_files: List[Path],
                       top_section: str = "Referencia", subgroup: str | None = "API") -> None:
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    data = {}
    if mkdocs_path.exists():
        with mkdocs_path.open("r", encoding="utf-8") as f:
            data = yaml.load(f) or {}

    # asegúrate de que hay una clave 'nav' lista
    nav = data.get("nav")
    if nav is None:
        nav = []
        data["nav"] = nav

    # construimos lista de rutas relativas para mkdocs
    rel_paths = [str(p.relative_to(docs_root).as_posix()) for p in md_files]
    rel_paths.sort()

    # construir estructura: {top_section: {subgroup: [ {Title: path}, ... ]}}
    def title_from_path(p: str) -> str:
        return Path(p).stem.replace("_", " ").title()

    items = [{title_from_path(p): p} for p in rel_paths]

    # buscar o crear sección principal
    def find_section(nav_list, key):
        for i, item in enumerate(nav_list):
            if isinstance(item, dict) and key in item:
                return i, item[key]
        return None, None

    idx, section_val = find_section(nav, top_section)
    if idx is None:
        # crear
        if subgroup:
            section_val = [{subgroup: items}]
        else:
            section_val = items
        nav.append({top_section: section_val})
    else:
        # existe
        if subgroup:
            # buscar subgroup dentro
            sub_idx, sub_val = find_section(section_val, subgroup) if isinstance(section_val, list) else (None, None)
            if sub_idx is None:
                # añadir subgroup nuevo
                if isinstance(section_val, list):
                    section_val.append({subgroup: items})
                else:
                    # caso raro, normaliza a lista
                    data["nav"][idx] = {top_section: [{subgroup: items}]}
            else:
                # reemplazar por completo el grupo (idempotente)
                section_val[sub_idx] = {subgroup: items}
        else:
            # reemplazar lista de items
            if isinstance(section_val, list):
                data["nav"][idx] = {top_section: items}
            else:
                data["nav"][idx] = {top_section: items}

    # escribir de vuelta
    with mkdocs_path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f)

# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser(description="Generate Markdown docs and update mkdocs.yml nav")
    ap.add_argument("--src", type=Path, required=True, help="Folder with Python source (package root)")
    ap.add_argument("--out", type=Path, required=True, help="Docs output folder, e.g., docs/reference")
    ap.add_argument("--mkdocs", type=Path, default=Path("mkdocs.yml"), help="Path to mkdocs.yml")
    ap.add_argument("--section", type=str, default="Referencia", help="Top-level nav section name")
    ap.add_argument("--group", type=str, default="API", help="Subgroup inside the section (set empty to disable)")
    ap.add_argument("--include-comments", action="store_true", help="Include # comments index")
    ap.add_argument("--no-mirror", action="store_true", help="Do NOT mirror package folder structure")
    args = ap.parse_args()

    md_files = generate_docs(
        src_dir=args.src,
        out_dir=args.out,
        include_comments=args.include_comments,
        mirror_tree=not args.no_mirror
    )

    subgroup = args.group if args.group else None
    update_mkdocs_yaml(args.mkdocs, args.out.resolve(), md_files,
                       top_section=args.section, subgroup=subgroup)

    print(f"[OK] Generated {len(md_files)} markdown files into {args.out}")
    print(f"[OK] mkdocs.yml updated under section '{args.section}'"
          + (f" → '{subgroup}'" if subgroup else ""))

if __name__ == "__main__":
    main()
