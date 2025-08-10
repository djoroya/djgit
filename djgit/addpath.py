import sys
import os
import argparse
import sysconfig
import site
from typing import Optional, List


def _find_site_packages() -> Optional[str]:
    """
    Try several strategies to find an appropriate site-packages/dist-packages directory
    for the current interpreter/environment. Returns the first existing path found.
    """
    candidates: List[str] = []

    # sysconfig is the most reliable
    for key in ("purelib", "platlib"):
        p = sysconfig.get_paths().get(key)
        if p:
            candidates.append(p)

    # site module (may return multiple entries)
    try:
        candidates.extend(site.getsitepackages())
    except Exception:
        pass  # not always available (e.g., virtualenvs on some platforms)

    # user site packages
    try:
        usp = site.getusersitepackages()
        if usp:
            candidates.append(usp)
    except Exception:
        pass

    # Fallback: scan sys.path
    for x in sys.path:
        if isinstance(x, str) and ("site-packages" in x or "dist-packages" in x):
            candidates.append(x)

    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            uniq.append(c)

    for c in uniq:
        if os.path.isdir(c):
            return c
    return None


def _normalize(p: str) -> str:
    """Normalize path for comparison (absolute + OS case rules)."""
    return os.path.normcase(os.path.abspath(p))


def addpath_python(path: str) -> None:
    """
            Adds a custom path to Python's search path (<code>sys.path</code>) by creating or updating a
        <code>.pth</code> file inside the active environment's <code>site-packages</code> directory.
        This allows modules in non-standard locations to be imported without setting
        environment variables every session.
<table>
  <thead>
    <tr>
      <th>Section</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Inputs</strong></td>
      <td>
        <code>--path</code> (<em>str</em>): Absolute or relative path to add to the PYTHONPATH.
      </td>
    </tr>
    <tr>
      <td><strong>Outputs</strong></td>
      <td>
        None (prints status messages to stdout and updates the <code>conda.pth</code> file).
      </td>
    </tr>
  </tbody>
</table>

<ul>
    <li>The <code>.pth</code> file is created in the first <code>site-packages</code> found in <code>sys.path</code>.</li>
    <li>If the path already exists in the file, it will not be duplicated.</li>
</ul>
<p>Example usage:</p>
```bash
djgit_addpath --path /path/to/my/path
```


"""
    print("Adding the following path to the PYTHONPATH:")
    print(path)

    # 1) Verify the path exists
    if not os.path.exists(path):
        print(f"[ERROR] Path {path} does not exist.")
        return

    cmd_abs = _normalize(path)

    # 2) Locate a suitable site-packages/dist-packages directory
    site_dir = _find_site_packages()
    if not site_dir:
        print("[ERROR] No 'site-packages' / 'dist-packages' directory found for this interpreter.")
        return

    print(f"Using site-packages directory: {site_dir}")

    # 3) Target .pth file
    pth_file = os.path.join(site_dir, "conda.pth")

    # Ensure file exists
    try:
        if not os.path.exists(pth_file):
            # Create empty file
            with open(pth_file, "a", encoding="utf-8"):
                pass
    except OSError as e:
        print(f"[ERROR] Could not create {pth_file}: {e}")
        return

    # 4) Read existing entries and detect duplicates (normalized)
    try:
        with open(pth_file, "r", encoding="utf-8") as f:
            raw_lines = [line.strip() for line in f.readlines() if line.strip()]
    except OSError as e:
        print(f"[ERROR] Could not read {pth_file}: {e}")
        return

    existing_norm = {_normalize(line) for line in raw_lines}

    if cmd_abs in existing_norm:
        print(f"[INFO] Path already present in {pth_file}: {cmd_abs}")
        return

    # 5) Append the normalized absolute path
    try:
        with open(pth_file, "a", encoding="utf-8") as f:
            f.write(cmd_abs + "\n")
    except OSError as e:
        print(f"[ERROR] Could not write to {pth_file}: {e}")
        return

    print(f"[OK] Path successfully added to {pth_file}")
    print(f"[OK] Added: {cmd_abs}")


def addpath() -> None:
    """
    Main function that parses command-line arguments and calls
    `addpath_python()` with the provided path.
    """
    parser = argparse.ArgumentParser(
        description="Add custom paths to PYTHONPATH via a .pth file"
    )
    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Path to add to the PYTHONPATH",
    )
    args = parser.parse_args()

    addpath_python(args.path)


if __name__ == "__main__":
    addpath()
