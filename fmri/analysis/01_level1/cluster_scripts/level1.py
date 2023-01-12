#! /opt/miniconda-4.10.3/bin/python

from argparse import ArgumentParser
from level1_utils import run_level1
import os

parser = ArgumentParser()
parser.add_argument("--subnum", help="subject number")
parser.add_argument("--session", help="session number")
parser.add_argument("--task", help="task name")
parser.add_argument("--mnum", help="model number")
parser.add_argument("--space", help="output space as defined in TemplateFlow")

args = parser.parse_args()

subnum = args.subnum
session = args.session
task = args.task
mnum = args.mnum
space = args.space

# determined in run_level1.batch docker call `docker run --rm -e DATA_PATH=/data -e OUT_PATH=/out`
data_path = os.environ['DATA_PATH']
out_path = os.environ['OUT_PATH']

run_level1(subnum, session, task, mnum, data_path, out_path, space)
