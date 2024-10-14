import os,shutil
from djgit.tools import get_repo_name, list_remote_branches,create_deploy_branch,clonar_deploy_branch
import json

def create_package_json(path,repo_name,target_path=".repo_deploy"):


    package_json = json.load(open(path))
    package_json["name"] = repo_name
    package_json["main"] = "index.js"
    if "private" in package_json.keys():
        del package_json["private"]

    package_json["scripts"] = {
    "test": "echo \"Error: no test specified\" && exit 1",
    "build": "babel src --out-dir .",
    "start": "node index.js"
    }
    package_json["author"] = "Deyviss Jesus Oroya Villalta"
    package_json["license"] = "MIT"

    with open(os.path.join(target_path,"package.json"), "w") as f:
        json.dump(package_json, f, indent=4)
    print(package_json)


def npm_deploy():

    folder_exists = os.path.exists('.repo_deploy')
    if not folder_exists:
        os.makedirs('.repo_deploy')


    repo_url,name = get_repo_name()
    remote_branches = list_remote_branches(repo_url)
    print("Ramas remotas:", remote_branches)

    if not "deploy" in remote_branches:

        print("La rama 'deploy' no existe en el repositorio remoto")
        create_deploy_branch(repo_url)

    else:
        print("La rama 'deploy' existe en el repositorio remoto")



    listdir = os.listdir(".repo_deploy")
    if not ".git" in listdir:
        print("Clonando la rama 'deploy' del repositorio remoto")
        #
        clonar_deploy_branch(repo_url)
        # remove .repo_deploy/*  remove all files in .repo_deploy except file initialized by .
        shutil.rmtree('.repo_deploy/scripts', ignore_errors=True)
        shutil.rmtree('.repo_deploy/src', ignore_errors=True)
    else:
        print("La rama 'deploy' ya ha sido clonada")


    create_package_json("package.json",name)

    # create .babelrc


    babel = {
    "presets": [
        "@babel/preset-env",
        "@babel/preset-react"
    ]
    }

    with open(os.path.join(".repo_deploy",".babelrc"), "w") as f:
        json.dump(babel, f, indent=4)

    copyfiles = ["README.md", "LICENSE", ".gitignore"]

    for file in copyfiles:
        shutil.copy(file, os.path.join(".repo_deploy", file))


    # copy all src/dependencies to .repo_deploy/src

    # create src folder in .repo_deploy if not exists
    if os.path.exists(os.path.join(".repo_deploy","src")):
        shutil.rmtree(os.path.join(".repo_deploy","src"))

    # cp -r src/dependencies/* .repo_deploy/src/.
    shutil.copytree(os.path.join("src","dependencies"),
                    os.path.join(".repo_deploy","src"))

    os.chdir('.repo_deploy')
    os.system("pwd")
    os.system('npm install react react-dom --save-peer')
    babel_dev = ["@babel/preset-react", 
                "@babel/preset-env", 
                "@babel/cli", 
                "@babel/core"]
    os.system('npm install ' + ' '.join(babel_dev) + ' --save-dev')
    os.system('npm run build')
