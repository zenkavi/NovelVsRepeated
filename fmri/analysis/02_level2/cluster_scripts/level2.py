#! /opt/miniconda-4.10.3/bin/python

from argparse import ArgumentParser
from level2_utils import run_level2
import os

#Usage: ./level3.py -m MNUM -r REG -s SIGN -tf TFCE

parser = ArgumentParser()
parser.add_argument("--mnum", help="model number")
parser.add_argument("--session", help="model name",)
parser.add_argument("-r", "--reg", help="regressor name")
parser.add_argument("-np", "--num_perm", help="number of permutations", default=5000)
parser.add_argument("-vs", "--var_smooth", help="variance smoothing", default=5)
parser.add_argument("-s", "--sign", help="calculate p values for positive or negative t's")
args = parser.parse_args()

mnum = args.mnum
session = args.session
reg = args.reg

num_perm = int(args.num_perm)
var_smooth = int(args.var_smooth)
sign = args.sign

data_path = os.environ['DATA_PATH']
out_path = os.environ['OUT_PATH']

run_level2(mnum, session, reg, sign, data_path, out_path, num_perm=num_perm, var_smooth=var_smooth)
