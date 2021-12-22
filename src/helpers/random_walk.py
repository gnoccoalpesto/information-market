from math import cos, radians, pi
import numpy as np

__crw_weights = []
__levi_weights = []
__max_levi_steps = 1000


def crw_pdf(thetas, rdwalk_factor):
    res = []
    for t in thetas:
        num = (1 - rdwalk_factor ** 2)
        denom = 2 * pi * (1 + rdwalk_factor ** 2 - 2 * rdwalk_factor * cos(radians(t)))
        f = 1
        if denom != 0:
            f = num / denom
        res.append(f)
    return res


def levi_pdf(max_steps, alpha):
    pdf = [step ** (-alpha - 1) for step in range(1, max_steps + 1)]
    return pdf


def set_parameters(random_walk_factor, levi_factor, max_levi_steps=1000):
    global __crw_weights, __levi_weights
    thetas = np.arange(0, 360)
    __crw_weights = crw_pdf(thetas, random_walk_factor)
    __levi_weights = levi_pdf(max_levi_steps, levi_factor)


def get_crw_weights():
    return __crw_weights


def get_levi_weights():
    return __levi_weights


def get_max_levi_steps():
    return __max_levi_steps