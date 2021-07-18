from lib import *
from math import radians, sin, cos

SWITCH_RISER_RADIUS = 0.8
SWITCH_RISER_HEIGHT = 9.0


def switch_riser_raw_dot_fn():
    return sphere(SWITCH_RISER_RADIUS)


switch_riser_raw_dot = switch_riser_raw_dot_fn()

top_dot = translate(0, 0, SWITCH_RISER_HEIGHT)(switch_riser_raw_dot)

def switch_riser_post_fn():
    post = translate(0, 0, SWITCH_RISER_HEIGHT / 2)(
        cylinder(SWITCH_RISER_RADIUS, SWITCH_RISER_HEIGHT, center=True)
    )

    return union(post, top_dot)


switch_riser_post = switch_riser_post_fn()
