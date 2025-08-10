# djgit
Creación de la carpeta de scripts
Primero, crea una carpeta llamada scripts en el directorio raíz de tu proyecto:

```bash
mkdir scripts
```
Luego, dentro de la carpeta scripts, crea un archivo Python llamado deploy.py con el siguiente contenido:

```python
import os
from djgit.deploy import deploy
```
# Especifica la carpeta de destino, partiendo desde el directorio raíz del proyecto

```
target_folder = os.path.join('src', 'dev', 'trial')  
deploy(target_folder)
```
En este ejemplo, target_folder es la ruta donde se ubica el código que deseas desplegar. Debes ajustarla según la estructura de tu proyecto.

Ejecución del despliegue
Para desplegar el proyecto, ejecuta el siguiente comando en la terminal:

```bash
python scripts/deploy.py
```
Al ejecutar este comando, se creará una nueva carpeta llamada .repo_deploy dentro del directorio del proyecto. Esta carpeta contendrá el código preparado para ser enviado a un nuevo branch en tu sistema de control de versiones, denominado "deploy".

Instalación de la librería en un nuevo proyecto
Si deseas instalar esta librería en otro proyecto, puedes hacerlo agregando la siguiente línea en tu archivo requirements.txt o ejecutando el comando pip install con la siguiente sintaxis:

```perl
djgit @ git+https://github.com/USERNAME/REPO_NAME.git@deploy
```
Asegúrate de reemplazar USERNAME y REPO_NAME con el nombre de usuario y el nombre del repositorio correspondientes en GitHub.
