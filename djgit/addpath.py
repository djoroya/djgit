import sys,os
import argparse
def addpath():

    parser = argparse.ArgumentParser(description='Add paths to the python path')
    parser.add_argument('--path', type=str, help='Path to add to the python path', default=path)
    args = parser.parse_args()

    path = args.path

    print("Adding the following paths to the python path:")
    print(path)

    # verify if the path exists
    if not os.path.exists(path):
        print(f"Path {path} does not exist")
        return
    
    # select the elements of path list who  contains the word 'site-packages'
    site = [x for x in sys.path if 'site-packages' in x]

    # take current working directory
    cwd = sys.path[0] 
    # add src

    cmd =  os.path.join(cwd, path) 

    print("Adding the following paths to the python path:")
    print(cmd)
    # create a new file named conda.pth in the site-packages directory
    with open(os.path.join(site[0], 'conda.pth'), 'a') as f:
        f.write(cmd)
        f.write('\n')

