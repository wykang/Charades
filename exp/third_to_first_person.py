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
name = __file__.split('/')[-1].split('.')[0]  # name is filename

args = [
    '--name', name, 
    '--print-freq', '1',
    '--train-file', './datasets/labels/CharadesEgo_v1_train.csv',
    '--val-file', './datasets/labels/CharadesEgo_v1_test.csv',
    '--dataset', 'charadesego',
    '--data', '/scratch/gsigurds/CharadesEgo_v1_rgb/',
    '--arch', 'ActorObserverBaseNoShare',
    '--subarch', 'resnet152',
    '--pretrained-subweights', '/nfs.yoda/gsigurds/charades_pretrained/resnet_rgb.pth.tar',
    '--loss', 'ActorObserverLossAll',
    '--subloss', 'DistRatio',
    '--decay', '0.95',
    '--lr', '3e-5',
    '--lr-decay-rate', '15',
    '--batch-size', '15',
    '--train-size', '0.2',
    '--val-size', '0.5',
    '--cache-dir', '/nfs.yoda/gsigurds/ai2/caches/',
    '--epochs', '50',
    # '--evaluate',
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
    print ''
    pdb.post_mortem()
    sys.exit(1)
