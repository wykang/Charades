"""
    Defines tasks for evaluation
"""
import torch
import numpy as np
import random
from itertools import groupby
from train import parse
from utils.utils import MedianMeter, Timer
from models.ActorObserverFC7 import ActorObserverFC7


def fc7list2mat(grp, dist=lambda x, y: np.linalg.norm(x - y)):
    ids, fc7s = zip(*list(grp))
    third, first = zip(*fc7s)
    n = len(ids)
    mat = np.zeros((n, n))
    for i, x in enumerate(third):
        for j, y in enumerate(first):
            mat[i, j] = dist(x, y)
    return ids, mat


def matsmooth(mat, winsize):
    m, n = mat.shape
    out = mat.copy()
    for aa in range(m):
        for bb in range(n):
            a = max(0, aa - winsize)
            a2 = min(m, aa + winsize + 1)
            b = max(0, bb - winsize)
            b2 = min(n, bb + winsize + 1)
            out[aa, bb] = mat[a:a2, b:b2].mean()
    return out


def best_one_sec_moment(mat, winsize=6):
    # assuming 6 fps
    m, n = mat.shape
    mat = matsmooth(mat, winsize)
    i, j = random.choice(np.argwhere(mat == mat.min()))
    gt = i / float(m) * n / 6.
    return i / float(m), j / float(n), i / 6., j / 6., gt


def alignment(loader, model, epoch, args, task=best_one_sec_moment):
    timer = Timer()
    abssec = MedianMeter()
    abssec0 = MedianMeter()
    randsec = MedianMeter()
    model = ActorObserverFC7(model)

    # switch to evaluate mode
    model.eval()

    def fc7_generator():
        for i, x in enumerate(loader):
            inputs, target, meta = parse(x)
            target = target.long().cuda(async=True)
            input_vars = [torch.autograd.Variable(inp.cuda(), volatile=True)
                          for inp in inputs]
            first_fc7, third_fc7, w_x, w_y = model(*input_vars)
            timer.tic()
            if i % args.print_freq == 0:
                print('Alignment: [{0}/{1}]\t'
                      'Time {timer.val:.3f} ({timer.avg:.3f})'.format(
                          i, len(loader), timer=timer))
            for vid, o1, o2 in zip(meta['id'], first_fc7, third_fc7):
                yield vid, (o1.data.cpu().numpy(), o2.data.cpu().numpy())

    for key, grp in groupby(fc7_generator(), key=lambda x: x[0]):
        print('processing id: {}'.format(key))
        _, mat = fc7list2mat(grp)
        _, _, _, j, gt = task(mat, winsize=3)
        _, _, _, j0, gt0 = task(mat, winsize=0)
        _, _, _, jr, gtr = task(np.random.randn(*mat.shape), winsize=3)
        abssec.update(abs(j - gt))
        abssec0.update(abs(j0 - gt0))
        randsec.update(abs(jr - gtr))
        print('  abs3: {abs3.val:.3f} ({abs3.avg:.3f}) [{abs3.med:.3f}]'
              '  abs0: {abs0.val:.3f} ({abs0.avg:.3f}) [{abs0.med:.3f}]'
              '\n'
              '  absr: {absr.val:.3f} ({absr.avg:.3f}) [{absr.med:.3f}]'.format(
                  abs3=abssec, abs0=abssec0, absr=randsec))

    return abssec.med


