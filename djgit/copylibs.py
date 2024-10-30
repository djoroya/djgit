import importlib
import os, shutil

def main():

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
        import shutil
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
    dirs = [d for d in dirs if d not in [".conda", ".vscode", ".git", ".repo_deploy", ".copylibs","requirements_temp.txt","simulations"]]

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