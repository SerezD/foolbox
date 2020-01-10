import eagerpy as ep
import numpy as np
import torch
import torch.nn as nn

from foolbox.ext.native.models import PyTorchModel
from foolbox.ext.native.attacks import L2AdditiveGaussianNoiseAttack
from foolbox.ext.native.attacks import L2RepeatedAdditiveGaussianNoiseAttack


def misclassification(
    inputs: ep.Tensor, labels: ep.Tensor, perturbed: ep.Tensor, logits: ep.Tensor
) -> ep.Tensor:
    classes = logits.argmax(axis=-1)
    return classes != labels


def test_additive_gaussian_noise_attack():
    channels = 3
    batch_size = 8
    h = w = 32
    bounds = (0, 1)

    class Model(nn.Module):
        def forward(self, x):
            x = torch.mean(x, 3)
            x = torch.mean(x, 2)
            return x

    model = Model().eval()
    fmodel = PyTorchModel(model, bounds=bounds)

    np.random.seed(0)
    x = np.random.uniform(*bounds, size=(batch_size, channels, h, w)).astype(np.float32)
    x = torch.from_numpy(x).to(fmodel.device)
    y = fmodel.forward(x).argmax(axis=-1)

    attack = L2AdditiveGaussianNoiseAttack(fmodel)
    advs = attack(x, y, epsilon=20.0)

    y_advs = fmodel.forward(advs).argmax(axis=-1)

    assert x.shape == advs.shape
    assert (y_advs == y).float().mean() < 0.8


def test_repeated_additive_gaussian_noise_attack():
    channels = 3
    batch_size = 8
    h = w = 32
    bounds = (0, 1)

    class Model(nn.Module):
        def forward(self, x):
            x = torch.mean(x, 3)
            x = torch.mean(x, 2)
            return x

    model = Model().eval()
    fmodel = PyTorchModel(model, bounds=bounds)

    np.random.seed(0)
    x = np.random.uniform(*bounds, size=(batch_size, channels, h, w)).astype(np.float32)
    x = torch.from_numpy(x).to(fmodel.device)
    y = fmodel.forward(x).argmax(axis=-1)

    attack = L2RepeatedAdditiveGaussianNoiseAttack(fmodel)
    advs = attack(x, y, epsilon=20.0, criterion=misclassification)

    y_advs = fmodel.forward(advs).argmax(axis=-1)

    assert x.shape == advs.shape
    assert (y_advs == y).float().mean() < 0.5
