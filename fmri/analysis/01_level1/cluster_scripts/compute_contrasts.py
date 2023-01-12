#! /opt/miniconda-4.10.3/bin/python

from argparse import ArgumentParser
from compute_contrast_utils import compute_contrasts
import os

parser = ArgumentParser()
parser.add_argument("--subnum", help="subject number")
parser.add_argument("--session", help="session number")
parser.add_argument("--task", help="task name")
parser.add_argument("--mnum", help="model number")
parser.add_argument("--contrasts_fn", help='contrasts file name')
parser.add_argument("--output_type", default='effect_size')
parser.add_argument("--output_space", help="output space as defined in TemplateFlow")


args = parser.parse_args()

subnum = args.subnum
session = args.session
task = args.task
mnum = args.mnum
contrasts_fn = args.contrasts_fn

output_type = args.output_type
output_space = args.output_space

# determined in run_level1.batch docker call `docker run --rm -e DATA_PATH=/data -e OUT_PATH=/out`
data_path = os.environ['DATA_PATH']
out_path = os.environ['OUT_PATH']

compute_contrasts(subnum, session, task, mnum, contrasts_fn, out_path, output_type = output_type, space = output_space)
