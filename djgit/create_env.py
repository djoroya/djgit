import os 
import argparse

path_folder = __file__.rsplit("/", 1)[0]

create_env_sh = os.path.join(path_folder, "create_env.sh")
add_path_sh = os.path.join(path_folder, "add_path_env.sh")

print(f"Path folder: {create_env_sh}")

def main():
    # --path 
    # --python

    parser = argparse.ArgumentParser(description="Create a virtual environment and install dependencies.")

    parser.add_argument(
        "--path",
        type=str,
        required=True,
        default=None,
        help="Path to the folder where the virtual environment will be created.",
    )

    parser.add_argument(
        "--python",
        type=str,
        default="3.9",
        help="Python interpreter to use for creating the virtual environment.",
    )

    args = parser.parse_args()

    path = args.path

    python = args.python

        
    os.system(f"sh {create_env_sh} {python}") 


    if path is not None:
        os.system(f"sh {add_path_sh} {path}")
