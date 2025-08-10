import os 
import argparse

path_folder = __file__.rsplit("/", 1)[0]

create_env_sh = os.path.join(path_folder, "create_env.sh")
add_path_sh = os.path.join(path_folder, "add_path_env.sh")

print(f"Path folder: {create_env_sh}")

LICENSE = """
Copyright 2025 Deyviss Jesus Oroya Villalta

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

def main():
    # --path 
    # --python

    parser = argparse.ArgumentParser(description="Create a virtual environment and install dependencies.")


    parser.add_argument(
        "--python",
        type=str,
        default="3.9",
        help="Python interpreter to use for creating the virtual environment.",
    )

    args = parser.parse_args()


    python = args.python

    os.system("mkdir -p src")
    # create requirements.txt if not exists
    if not os.path.exists("requirements.txt"):
        with open("requirements.txt", "w") as f:
            f.write("# Add your project dependencies here\n")
    os.system("mkdir -p scripts")
    # README.md
    if not os.path.exists("README.md"):
        with open("README.md", "w") as f:
            f.write("# Project Title\n\nDescription of the project.\n")
    
    # Create settings folder 
    if not os.path.exists("settings"):
        os.makedirs("settings")

        # copy create_env.sh and add_path_env.sh to settings with name INSTALL.sh

        os.system(f"cp {create_env_sh} settings/INSTALL.sh")

        print(" Run the following command to install the virtual environment:")
        print(50 * "-")
        print(f"   sh settings/INSTALL.sh")
        print(50 * "-")
    # mkdir src 
