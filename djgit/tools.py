import shutil,os

def list_remote_branches(repo_url):
    # Ejecutar el comando 'git ls-remote --heads' para listar las ramas remotas
    command = f'git ls-remote --heads {repo_url}'
    stream = os.popen(command)
    output = stream.read()

    # Procesar la salida para extraer los nombres de las ramas
    branches = []
    for line in output.splitlines():
        # Cada línea tiene el formato 'hash refs/heads/branch_name'
        parts = line.split()
        if len(parts) == 2 and parts[1].startswith('refs/heads/'):
            branch_name = parts[1].replace('refs/heads/', '')
            branches.append(branch_name)

    return branches


def create_deploy_branch(repo_url):
    # Crear la rama 'deploy' en el repositorio remoto
    command = f'git push {repo_url} HEAD:refs/heads/deploy'
    stream = os.popen(command)
    output = stream.read()
    print(output)

def clonar_deploy_branch(repo_url):
    # Clonar la rama 'deploy' del repositorio remoto
    command = f'git clone -b deploy {repo_url} .repo_deploy'
    stream = os.popen(command)
    output = stream.read()

    print(output)

def get_repo_name():
    stream = os.popen('git remote -v')
    output = stream.read()
    repo_url =  output.split("\n")[0].split("\t")[1].split(" ")[0]
    name = repo_url.split("/")[-1].replace(".git","")
    return repo_url,name

import os,shutil

def createsetup(repo_name):

    setup_lines = """  
from setuptools import setup, find_packages

setup(
    name="REPO_NAME",
    version="0.1.0",
    description="",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Deyviss Jesus Oroya Villalta",
    author_email="djoroya@gmail.com",
    url="https://github.com/djoroya/REPO_NAME",
    packages=find_packages(),  # Encuentra  los paquetes en la carpeta src
    project_urls={
        "Source Code": "https://github.com/djoroya/REPO_NAME",
        "Bug Tracker": "https://github.com/djoroya/REPO_NAME/issues",
    },
    # from requeriments.txt
    install_requires=open('requirements.txt').read().splitlines(),
    python_requires='>=3.6',  #   de Python requerida
    classifiers=[  # Clasificadores que ayudan a otros desarrolladores a encontrar tu proyecto
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Tipo de licencia
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_data={
    },
)
  """

    setup_lines = setup_lines.replace("REPO_NAME", repo_name)

    # 
    # write setup.py

    with open( "setup.py", "w") as f:
        f.write(setup_lines)
        print(f"File setup.py created with success")