#!/bin/bash
#  $1 path
eval "$(conda shell.bash hook)"
conda activate .conda
djgit_addpath --path "$1"

