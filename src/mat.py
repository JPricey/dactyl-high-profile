import numpy as np
from math import radians, sin, cos

def point3(x, y, z):
    return np.transpose(np.array([x,y,z,1]))

def vec3(x, y, z):
    return np.transpose(np.array([[x,y,z,0]]))

def to_point(pv):
    return pv.tolist()[:-1]

def translate(x, y, z):
    return np.array([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1],
    ])

def scale(x, y, z):
    return np.array([
        [x, 0, 0, 0],
        [0, y, 0, 0],
        [0, 0, z, 0],
        [0, 0, 0, 1],
    ])

def identity():
    return scale(1,1,1)

def rotate_x(deg):
    rad = radians(deg)
    return np.array([
        [1, 0, 0, 0],
        [0, cos(rad), -sin(rad), 0],
        [0, sin(rad), cos(rad), 0],
        [0, 0, 0, 1],
    ])


def rotate_y(deg):
    rad = radians(deg)
    return np.array([
        [cos(rad), 0, sin(rad), 0],
        [0, 1, 0, 0],
        [-sin(rad), 0, cos(rad), 0],
        [0, 0, 0, 1],
    ])

def rotate_z(deg):
    rad = radians(deg)
    return np.array([
        [cos(rad), -sin(rad), 0, 0],
        [sin(rad), cos(rad), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])

def compose(*mats):
    result = identity()
    for m in mats:
        result = m @ result
    return result
