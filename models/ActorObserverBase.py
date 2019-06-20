"""
ActorObserver Base model
"""
import torch
import torch.nn as nn
import math
import torch.nn.functional as F
from models.utils import dprint, load_sub_architecture, remove_last_layer


class ActorObserverModel(nn.Module):
    def __init__(self, basenet):
        super(ActorObserverModel, self).__init__()
        self.basenet = basenet
        dim = basenet.outdim
        self.firstpos_fc = nn.Sequential(nn.Linear(dim, 1), nn.Tanh())
        self.third_fc = nn.Sequential(nn.Linear(dim, 1), nn.Tanh())
        self.firstneg_fc = self.firstpos_fc
        self.firstpos_scale = nn.Parameter(torch.Tensor([math.log(.5)]))
        self.third_scale = nn.Parameter(torch.Tensor([math.log(.5)]))
        self.firstneg_scale = nn.Parameter(torch.Tensor([math.log(.5)]))

    def base(self, x, y, z):
        base_x = self.basenet(x)
        base_y = self.basenet(y)
        base_z = self.basenet(z)
        dist_a = F.pairwise_distance(base_x, base_y, 2).view(-1)
        dist_b = F.pairwise_distance(base_y, base_z, 2).view(-1)
        dprint('fc7 norms: {} \t {} \t {}', base_x.data.norm(), base_y.data.norm(), base_z.data.norm())
        dprint('pairwise dist means: {} \t {}', dist_a.data.mean(), dist_b.data.mean())
        return base_x, base_y, base_z, dist_a, dist_b

    def verbose(self):
        dprint('scales:{}\t{}\t{}',
               math.exp(self.firstpos_scale.data[0]),
               math.exp(self.third_scale.data[0]),
               math.exp(self.firstneg_scale.data[0]))

    def forward(self, x, y, z):
        """ assuming:
            x: first person positive
            y: third person
            z: first person negative
        """
        base_x, base_y, base_z, dist_a, dist_b = self.base(x, y, z)
        w_x = self.firstpos_fc(base_x).view(-1) * torch.exp(self.firstpos_scale)
        w_y = self.third_fc(base_y).view(-1) * torch.exp(self.third_scale)
        w_z = self.firstneg_fc(base_z).view(-1) * torch.exp(self.firstneg_scale)
        self.verbose()
        return dist_a, dist_b, w_x, w_y, w_z


class ActorObserverBase(ActorObserverModel):
    def __init__(self, args):
        model = load_sub_architecture(args)
        remove_last_layer(model)
        super(ActorObserverBase, self).__init__(model)
