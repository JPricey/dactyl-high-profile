import solid

default_segments = 18

class NativeSCAD():
    def __init__(self, solid_fn, *args, mat_apply = None, **kwargs):
        def build_solid_fn():
            return solid_fn(*args, **kwargs)
        self.solid = build_solid_fn

    def __call__(self, other):
        assert isinstance(other, NativeSCAD)
        return Composer([self, other])

    def _apply_to(self, other):
        return self.compile()(other)

    def matrix_apply(self, point):
        assert self.mat_apply is not None

        return 

    def compile(self):
        return self.solid()

class Composer(NativeSCAD):
    def __init__(self, children):
        assert len(children) > 0
        self.children = children

    def _apply_to(self, other):
        result = other
        for c in reversed(self.children):
            result = c._apply_to(result)
        return result

    def compile(self):
        result = self.children[-1].compile()
        for c in reversed(self.children[:-1]):
            result = c._apply_to(result)
        return result

class Merger(NativeSCAD):
    def __init__(self, solid_fn, children):
        self.solid = solid_fn
        self.children = children

    def __call__(self, other):
        raise 'Cannot call merger'

    def _apply_to(self, other):
        raise 'Cannot apply merger'

    def compile(self):
        return self.solid()(*[c.compile() for c in self.children])

def translate(x, y, z):
    return NativeSCAD(solid.translate, [x, y, z])

def identity():
    return translate(0, 0, 0)

def scale(x, y, z):
    return NativeSCAD(solid.scale, [x, y, z])

def rotate(*, a, v):
    return NativeSCAD(solid.rotate, a=a, v=v)

def rotate_x(a):
    return rotate(a=a, v=[1, 0, 0])

def rotate_y(a):
    return rotate(a=a, v=[0, 1, 0])

def rotate_z(a):
    return rotate(a=a, v=[0, 0, 1])

def mirror(x, y, z):
    return NativeSCAD(solid.mirror, [x, y, z])

def flip_lr():
    return mirror(-1, 0, 0)

def project(*args, **kwargs):
    return NativeSCAD(solid.projection, *args, **kwargs)

def offset(*args):
    return NativeSCAD(solid.offset, *args)

def extrude_linear(height):
    return NativeSCAD(solid.linear_extrude, height)

def colour(r, g, b, z):
    return NativeSCAD(solid.color, [r/ 255.0, g/ 255.0, b/ 255.0, z])

# Functional
def compose(*atoms):
    assert len(atoms) > 0
    return Composer(list(reversed(atoms)))

# Merges
def union(*children):
    return Merger(solid.union, children)

def hull(*children):
    return Merger(solid.hull, children)

def difference(*children):
    return Merger(solid.difference, children)

def intersection(*children):
    return Merger(solid.intersection, children)

# def projection(child):
#     return NativeSCAD(solid.projection, child)

#def linear_extrude

# Shapes
def cube(x, y, z, **kwargs):
    return NativeSCAD(solid.cube, [x, y ,z], **kwargs)

def cylinder(r, h, segments = default_segments, **kwargs):
    return NativeSCAD(solid.cylinder, r=r, h=h, segments=segments, **kwargs)

def cylinderr1r2(r1, r2, h, segments = default_segments, **kwargs):
    return NativeSCAD(solid.cylinder, r1=r1, r2=r2, h=h, segments=segments, **kwargs)

def sphere(r, segments = default_segments, **kwargs):
    return NativeSCAD(solid.sphere, r=r, segments=segments, **kwargs)

def square(x, y, **kwargs):
    return NativeSCAD(solid.square, [x, y], **kwargs)

def render_to_file(obj, filename):
    solid.scad_render_to_file(obj.compile(), filename)
