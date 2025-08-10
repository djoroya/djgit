#!/bin/bash
# $1 - python version (e.g., 3.9)
# $2 - path of dependecies folder (e.g., ./src)



eval "$(conda shell.bash hook)"
if [ -d ".conda" ]; then
    echo
    echo "|=======================================================================|"
    echo "|   El entorno Conda ya existe. Activando el entorno...                 |"
    echo "|   No se puede crear un entorno Conda en el directorio actual.         |"
    echo "|   Elimine el directorio .conda si desea crear uno nuevo.              |"
    echo "========================================================================|"
    echo 
    exit 1
else
    # Crear el entorno de conda en el directorio actual si no existe
    echo "Creando el entorno Conda..."
    conda create -p .conda/ python=3.9
fi

conda activate .conda/
conda install pip


pip install -r requirements.txt

pip install git+https://github.com/djoroya/djgit.git

mkdir -p src
djgit_addpath --path src

# create .gitignore file
echo ".conda/" > .gitignore
echo "*.pyc" >> .gitignore