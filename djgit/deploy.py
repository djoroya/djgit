import os
import shutil
from tools import get_repo_name, list_remote_branches, create_deploy_branch, clonar_deploy_branch,createsetup

# ============== Main ===================

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

# combrobamos que exista .git
    
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


target_folder = os.path.join('src', 'dev', 'trial')
copyfiles = ["README.md", "LICENSE", ".gitignore","requirements.txt"]
for file in copyfiles:
    shutil.copy(file, os.path.join(".repo_deploy", file))

# copy src/* to .repo_deploy/name of the repo
folder_name = os.path.join('.repo_deploy', name)
if os.path.exists(folder_name):
    shutil.rmtree(folder_name)

shutil.copytree(target_folder, folder_name)

os.chdir('.repo_deploy')
createsetup(name)

os.system('python setup.py sdist')
os.system('python setup.py bdist_wheel')
