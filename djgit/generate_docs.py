import os
import subprocess

SRC_DIR = "scripts"   # Carpeta donde guardas notebooks y scripts
DOCS_DIR = "docs"     # Carpeta donde se generará la doc


def ensure_dir(path: str):
    """Crea carpeta si no existe."""
    if not os.path.exists(path):
        os.makedirs(path)


def convert_notebook(nb_path: str, md_path: str):
    """Convierte un notebook .ipynb a markdown usando nbconvert."""
    subprocess.run([
        "jupyter", "nbconvert", "--to", "markdown", nb_path,
        "--output", os.path.splitext(os.path.basename(md_path))[0],
        "--output-dir", os.path.dirname(md_path)
    ])


def convert_script(py_path: str, md_path: str):
    """Extrae docstring de un .py y lo guarda en markdown."""
    with open(py_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    docstring = ""
    inside = False
    for line in lines:
        if '"""' in line or "'''" in line:
            inside = not inside
            continue
        if inside:
            docstring += line

    if not docstring.strip():
        docstring = "⚠️ No hay docstring."

    md_content = f"# {os.path.basename(py_path)}\n\n{docstring}\n"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)


def process_directory(src_dir: str, docs_dir: str):
    """Convierte todos los .ipynb y .py en markdown respetando estructura."""
    for root, _, files in os.walk(src_dir):
        rel_path = os.path.relpath(root, src_dir)
        out_dir = os.path.join(docs_dir, rel_path)
        ensure_dir(out_dir)

        for file in files:
            src_path = os.path.join(root, file)
            if file.endswith(".ipynb"):
                md_path = os.path.join(out_dir, file.replace(".ipynb", ".md"))
                convert_notebook(src_path, md_path)
            elif file.endswith(".py"):
                md_path = os.path.join(out_dir, file.replace(".py", ".md"))
                convert_script(src_path, md_path)


if __name__ == "__main__":
    ensure_dir(DOCS_DIR)
    process_directory(SRC_DIR, DOCS_DIR)
    print("✅ Documentación generada en", DOCS_DIR)
