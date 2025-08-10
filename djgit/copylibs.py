import importlib
import os, shutil

def main():
    """
Creates a timestamped snapshot of the current project by freezing dependencies, separating VCS-based packages from standard ones, vendoring importable VCS modules for pruning, and copying the working tree into <code>.copylibs/<timestamp></code>. Temporary files are cleaned up, and a consolidated <code>requirements.txt</code> is written inside the snapshot.
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
        None
      </td>
    </tr>
    <tr>
      <td><strong>Outputs</strong></td>
      <td>
        <em>str</em>: Path to the created snapshot directory (e.g., <code>.copylibs/2025-08-10-12-34-56</code>). Side effects include writing a cleaned <code>requirements.txt</code> inside the snapshot, creating/removing temporary files (<code>requirements_temp*.txt</code>), and creating/removing the <code>dependencies</code> folder.
      </td>
    </tr>
  </tbody>
</table>

<ul>
  <li>Runs <code>pip freeze</code> via <code>os.system</code>; requires <code>pip</code> available on <code>PATH</code>.</li>
  <li>Overwrites temporary files and deletes the <code>dependencies</code> directory if it exists.</li>
  <li>Import errors for VCS modules are caught and printed; those modules are skipped.</li>
  <li>Prunes <code>lammps</code> (for modules containing <code>djlmp</code>) and <code>simulations</code> (for modules containing <code>runstep</code>) after vendoring.</li>
  <li>File operations may raise <code>OSError</code> or <code>shutil.Error</code> depending on permissions and filesystem state.</li>
</ul>
<p>Example usage:</p>
```bash
djgit_copylibs  
```
"""

    os.system("pip freeze > requirements_temp.txt")
    def read_requirements():
        with open('requirements_temp.txt') as f:
            return f.read().splitlines()
        

    req_raw = read_requirements()
    # select git+

    req = [r.split("/")[-1].replace(".git","").split("@")[0] for r in req_raw if "git+" in r]

    req_no_git = [r for r in req_raw if "git+" not in r if "@" not in r]
    with open('requirements_temp_no_git.txt', 'w') as f:
        for item in req_no_git:
            f.write("%s\n" % item)

    # save in requirements_temp.txt
    with open('requirements_temp.txt', 'w') as f:
        for item in req:
            f.write("%s\n" % item)

    mods = []
    for r in req:

        r = "loadsavejson" if r == "loadjson" else r
        print(f"importing {r}")
        try:
            mod =importlib.import_module(r)
            mods.append({
                "name": mod.__name__,
                "path": mod.__path__,
            })
        except Exception as e:
            print(f"Error importing {r}: {e}")
            pass

    dev_folder = "dependencies"

    # remove is exists
    if os.path.exists(dev_folder):
        shutil.rmtree(dev_folder)
        
    print(f"creating {dev_folder}")
    os.makedirs(dev_folder, exist_ok=True)

    for mod in mods:
        print(f"copying {mod['name']} to {dev_folder}")
        print(mod['path'])
        print(f"{dev_folder}/{mod['name']}")
        shutil.copytree(mod['path'][0], f"{dev_folder}/{mod['name']}")

        if "djlmp" in mod['name']:
            if os.path.exists(f"{dev_folder}/{mod['name']}/lammps"):
                shutil.rmtree(f"{dev_folder}/{mod['name']}/lammps")
        if "runstep" in mod['name']:
            if os.path.exists(f"{dev_folder}/{mod['name']}/simulations"):
                shutil.rmtree(f"{dev_folder}/{mod['name']}/simulations")
    # add to gitignore


    # mkdir .copylibs 

    if not os.path.exists(".copylibs"):
        os.makedirs(".copylibs")

    # random name
    import datetime

    now = datetime.datetime.now()

    # mkdir .copylibs/2021-01-01-12-00-00
    now_str = now.strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs(f".copylibs/{now_str}")

    # list dirs 
    dirs = os.listdir(".")
    # remove .conda .vscode .git .repo_deploy .copylibs
    dirs = [d for d in dirs if d not in [".conda", 
                                         ".vscode", ".git", 
                                         ".repo_deploy", 
                                         ".copylibs",
                                         "node_modules",
                                         "requirements_temp.txt",
                                         "simulations"]]

    print(dirs)
    # copy others 

    for d in dirs:
        print(f"copying {d}")
        if os.path.isdir(d):
            shutil.copytree(f"{d}", f".copylibs/{now_str}/{d}")
        else:
            shutil.copy(f"{d}", f".copylibs/{now_str}/{d}")


    #  mv requirements_temp_no_git.txt requirements.txt
    shutil.move(f".copylibs/{now_str}/requirements_temp_no_git.txt", f".copylibs/{now_str}/requirements.txt")

    # remove requirements_temp.txt
    os.remove("requirements_temp.txt")
    # remove requirements_temp_no_git.txt
    os.remove("requirements_temp_no_git.txt")

    # remove dependencies
    shutil.rmtree("dependencies")

    return f".copylibs/{now_str}"