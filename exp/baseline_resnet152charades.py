#!/usr/bin/env python
import sys
import os
import subprocess
import traceback
import pdb
from bdb import BdbQuit
subprocess.Popen('find ./exp/.. -iname "*.pyc" -delete'.split())
sys.path.insert(0, '.')
os.nice(19)
from main import main

args = [
    '--name', __file__.split('/')[-1].split('.')[0],  # name is filename
    '--print-freq', '1',
    '--train-file', './datasets/labels/CharadesEgo_v1_train.csv',
    '--val-file', './datasets/labels/CharadesEgo_v1_test.csv',
    '--dataset', 'charadesego',
    '--data', './data/Charades_Ego/CharadesEgo_v1_rgb/',
    '--arch', 'ActorObserverBase',
    '--subarch', 'resnet152',
    #'--pretrained-subweights', '/nfs.yoda/gsigurds/charades_pretrained/resnet_rgb.pth.tar',
    '--loss', 'WeightedBaseline',
    '--subloss', 'DistRatio',
    '--batch-size', '20',
    '--train-size', '0.2',
    '--val-size', '0.5',
    '--cache-dir', './caches/',
    '--epochs', '50',
    '--nopdb',
    '--pretrained',
    '--evaluate',
    '--alignment',
    # '--usersalignment',
]
sys.argv.extend(args)
try:
    main()
except BdbQuit:
    sys.exit(1)
except Exception:
    traceback.print_exc()
    print ('')
    pdb.post_mortem()
    sys.exit(1)
