import sys,os,glob
import argparse

def addpath_python(path):
    print("Adding the following paths to the python path:")
    print(path)

    # verify if the path exists
    if not os.path.exists(path):
        print(f"Path {path} does not exist")
        return
    
    # select the elements of path list who  contains the word 'site-packages'
    site = [x for x in sys.path if 'site-packages' in x]

    cmd =  os.path.abspath(path)

    print("Adding the following paths to the python path:")
    print(cmd)

    # pth file 

    # es mejor crear un archivo pth nuevo 
    pth_file = os.path.join(site[0], 'conda.pth')

    # check if the path is already in the pth file
    with open(pth_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if cmd == line:
                print(f"Path {cmd} already in the pth file")
                return
            
    print("Path to the pth file:")
    print(pth_file)

    # create a new file named conda.pth in the site-packages directory
    with open(pth_file, 'a') as f:
        f.write(cmd)
        f.write('\n')


def addpath():

    parser = argparse.ArgumentParser(description='Add paths to the python path')
    parser.add_argument('--path', type=str, help='Path to add to the python path')
    args = parser.parse_args()

    path = args.path

    addpath_python(path)
    