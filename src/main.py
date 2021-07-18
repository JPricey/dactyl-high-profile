import datetime
from math import radians, sin, cos
from lib import *
from shapes import *
import lib
import mat

switch_thickness = 2.0
web_thickness = 1.5
switch_rim_thickness = 1.5

post_width = 0.5
post_rad = post_width / 2

keyhole_size = 14.4
keyswitch_height = 14
keyswitch_width = 14

plate_outer_width = keyhole_size + switch_rim_thickness * 2

max_num_rows = 4
num_cols = 6
num_pinky_columns = 2

cols_with_max_rows = [2, 3]

sa_profile_key_height = 12.7
cap_top_height = switch_thickness + sa_profile_key_height

# extra space between the base of keys
extra_height = 1.0
extra_width = 2.5
mount_height = keyswitch_height + 3.0
mount_width = keyswitch_width + 3.0
# use 10 for faster prototyping, 15 for real
tenting_angle = 10.0
z_offset = 8.0

should_include_risers = False

def is_pinky(col):
    return col >= num_cols - num_pinky_columns

# aka: alpha
def row_curve_deg(col):
    # I tried to have a different curve for pinkys, but it didn't work well
    return 17

# aka: beta
col_curve_deg = 4.0

column_radius = cap_top_height + ((mount_width + extra_width) / 2) / sin(radians(col_curve_deg) / 2)

def row_radius(col):
    return cap_top_height + ((mount_height + extra_height) / 2) / sin(radians(row_curve_deg(col)) / 2)

# default 3
# controls left-right tilt / tenting (higher number is more tenting)
center_col = 3
center_row = 1


def column_extra_transform(col):
    if is_pinky(col):
        # TODO: translate first?
        return compose(
            rotate_x(6),
            rotate_y(-3)
        )
    else:
        return identity()

def num_rows_for_col(col):
    if col in cols_with_max_rows:
        return max_num_rows
    else:
        return max_num_rows - 1

def does_coord_exist(row, col):
    return col >= 0 and col < num_cols and row >= 0 and row < num_rows_for_col(col)

def negative(vect):
    return [-x for x in vect]

def bottom_transform(height):
    return extrude_linear(height)(project())

def bottom_hull(shape):
    return hull(shape, bottom_transform(0.1)(shape))

def single_switch_fn():
    outer_width = keyhole_size + switch_rim_thickness * 2

    bottom_wall = cube(outer_width, switch_rim_thickness, switch_thickness)
    top_wall = translate(0, keyhole_size + switch_rim_thickness, 0)(bottom_wall)

    left_wall = cube(switch_rim_thickness, outer_width, switch_thickness)
    right_wall = translate(keyhole_size + switch_rim_thickness, 0, 0)(left_wall)


    nub_len = 2.75
    nub_cyl = translate(0, 0, -1)(rotate_x(90)(cylinder(1, nub_len, 30, center=True)))
    nub_cube = translate(-switch_rim_thickness / 2, 0, 0.)(cube(switch_rim_thickness, nub_len, 4, center=True))
    left_nub = translate(switch_rim_thickness, (outer_width) / 2, 0)(hull(nub_cyl, nub_cube))

    right_nub_cube = translate(switch_rim_thickness / 2, 0, 0)(cube(switch_rim_thickness, nub_len, 4, center=True))
    right_nub = translate(-switch_rim_thickness + outer_width, (outer_width) / 2, 0)(hull(nub_cyl, right_nub_cube))

    return translate(-outer_width/2, -outer_width/2, 0)(union(
            bottom_wall,
            top_wall,
            left_wall,
            right_wall,
            left_nub,
            right_nub,
            ))

single_switch = single_switch_fn()

filled_switch = translate(0, 0, switch_thickness / 2.0)(cube(plate_outer_width, plate_outer_width, switch_thickness, center=True))

sa_length = 18.25
sa_double_length = 37.5

def sa_cap_fn():
    # bl2 = sa_length / 2
    m = 17.0

    bot = square(sa_length, sa_length, center=True)
    bot = extrude_linear(0.1)(bot)

    mid = square(m, m, center=True)
    mid = extrude_linear(0.1)(mid)
    mid = translate(0, 0, 6)(mid)

    top = square(12, 12, center=True)
    top = extrude_linear(0.1)(top)
    top = translate(0, 0, 12)(top)

    return colour(220, 163, 163, 1)(translate(0, 0, 5 + switch_thickness)(hull(bot, mid, top)))

sa_cap = sa_cap_fn()

def row_cols():
    for row in range(max_num_rows):
        for col in range(num_cols):
            if row < num_rows_for_col(col):
                yield (row, col)

def all_of_shape(shape):
    return [grid_position(row, col, shape) for (row, col) in row_cols()]

web_post = translate(-post_rad, -post_rad, switch_thickness - web_thickness)(cube(post_width, post_width, web_thickness))
short_web_post = translate(-post_rad, -post_rad, 0)(cube(post_width, post_width, post_width))

SQUARE_OFFSET_IDXS = [
    [[-1, -1], [1, -1]],
    [[-1, 1], [1, 1]],
]

def square_apply(square, fn):
    return [[fn(x) for x in y] for y in square]

def square_translater_at_offset(offset):
    def fn(idx):
        return translate(idx[0] * offset, idx[1] * offset, 0)

    return square_apply(SQUARE_OFFSET_IDXS, fn)

def apply_translate_square(square, shape):
    def fn(translator):
        return translator(shape)
    return square_apply(square, fn)


outer_post_delta = keyhole_size / 2 + switch_rim_thickness # - post_rad/2

outer_post_translate_square = square_translater_at_offset(outer_post_delta)

web_post_tr = translate(outer_post_delta, outer_post_delta, 0)(web_post)
web_post_tl = translate(-outer_post_delta, outer_post_delta, 0)(web_post)
web_post_br = translate(outer_post_delta, -outer_post_delta, 0)(web_post)
web_post_bl = translate(-outer_post_delta, -outer_post_delta, 0)(web_post)

web_posts = apply_translate_square(outer_post_translate_square, web_post)
short_web_posts = apply_translate_square(outer_post_translate_square, short_web_post)

inner_post_delta = keyhole_size / 2 + post_rad
inner_post_translate_square = square_translater_at_offset(inner_post_delta)

inner_web_posts = apply_translate_square(inner_post_translate_square, web_post)
short_inner_web_posts = apply_translate_square(inner_post_translate_square, short_web_post)

post_left_edge_indexes = [[0, 0], [1, 0]]
post_top_edge_indexes = [[1, 0], [1, 1]]
post_right_edge_indexes = [[1, 1], [0, 1]]
post_bot_edge_indexes = [[0, 1], [0, 0]]

square_idx_tl = [1, 0]
square_idx_tr = [1, 1]
square_idx_bl = [0, 0]
square_idx_br = [0, 1]

def get_web_post(idx):
    return web_posts[idx[0]][idx[1]]

post_left_edge = [get_web_post(e) for e in post_left_edge_indexes]
post_top_edge = [get_web_post(e) for e in post_top_edge_indexes]
post_right_edge = [get_web_post(e) for e in post_right_edge_indexes]
post_bot_edge = [get_web_post(e) for e in post_bot_edge_indexes]

def get_in_square(square, idx):
    return square[idx[0]][idx[1]]

def get_inner_web_post(idx):
    return get_in_square(inner_web_posts, idx)

def get_short_web_post(idx):
    return get_in_square(short_web_posts, idx)

def get_short_inner_web_post(idx):
    return get_in_square(short_inner_web_posts, idx)


def column_offset(col):
     if col == 2:
         return [0, 5, -3]
     elif col == 3:
         return [0, 0, -0.5]
     elif is_pinky(col):
         return [1.0, -14.5, 5.0]
     else:
         return [0, 0, 0]

def col_z_rotate(col):
    if is_pinky(col):
        return -3.0
    else:
        return 0

def place_on_grid_base(row, column, domain):
    column_angle = col_curve_deg * (center_col - column)
    row_angle = row_curve_deg(column) * (center_row - row)

    return domain.compose(
            # Row Sphere
            domain.translate(0, 0, -row_radius(column)),
            domain.rotate_x(row_angle),
            domain.translate(0, 0, row_radius(column)),
            # Row Offset
            # column_extra_transform(column),
            # Col sphere
            domain.translate(0, 0, -column_radius),
            domain.rotate_y(column_angle),
            domain.translate(0, 0, column_radius),

            # Z Fix
            domain.rotate_z(col_z_rotate(column)),

            # Column offset
            domain.translate(*column_offset(column)),
            # Misc
            domain.rotate_y(tenting_angle),
            domain.translate(0, 0, z_offset),
            )

def place_on_grid(row, column):
    return place_on_grid_base(row, column, lib)

def point_on_grid(row, column, x, y, z):
    point = mat.point3(x, y, z)
    tx_point = place_on_grid_base(row, column, mat) @ point

    return tx_point[:3]

def grid_position(row, col, shape):
    return place_on_grid(row, col)(shape)

def connectors():
    def make_edge_connection(r1, c1, e1, r2, c2, e2):
        posts1 = [grid_position(r1, c1, e) for e in e1]
        posts2 = [grid_position(r2, c2, e) for e in e2]
        return hull(*posts1, *posts2)

    all_connectors = []
    for col in range(num_cols - 1):
        for row in range(max_num_rows):
            if does_coord_exist(row, col) and does_coord_exist(row, col + 1):
                if (row, col) == (0, 3):
                    right_edge = [translate(1, 1, 0)(web_post_tr), translate(0, 1, 0)(web_post_tr), web_post_br]
                else:
                    right_edge = post_right_edge
                all_connectors.append(make_edge_connection(row, col, right_edge, row, col + 1, post_left_edge))


    for col in range(num_cols):
        for row in range(max_num_rows - 1):
            if does_coord_exist(row, col) and does_coord_exist(row + 1, col):
                all_connectors.append(make_edge_connection(row, col, post_bot_edge, row+ 1, col, post_top_edge))

    for col in range(num_cols - 1):
        row = num_rows_for_col(col) - 1
        next_col = col + 1
        next_row = num_rows_for_col(next_col) - 1
        if next_row == row + 1:
            this_t = place_on_grid(row, col)
            next_t = place_on_grid(next_row, next_col)
            this_level_t = place_on_grid(row, next_col)
            all_connectors.append(
                    hull(
                        this_t(web_post_br),
                        this_level_t(web_post_bl),
                        next_t(web_post_tl),
                        )
                    )
            all_connectors.append(
                    hull(
                        this_t(web_post_br),
                        next_t(web_post_tl),
                        next_t(web_post_bl),
                        )
                    )
        if next_row == row - 1:
            this_t = place_on_grid(row, col)
            next_t = place_on_grid(next_row, next_col)
            this_level_t = place_on_grid(next_row, col)

            all_connectors.append(
                    hull(
                        this_t(web_post_tr),
                        this_level_t(web_post_br),
                        next_t(web_post_bl),
                        )
                    )

            all_connectors.append(
                    hull(
                        this_t(web_post_tr),
                        this_t(web_post_br),
                        next_t(web_post_bl),
                        )
                    )

    def does_diag_exist(row, col):
        for dr in [0, 1]:
            for dc in [0, 1]:
                if not does_coord_exist(row + dr, col + dc):
                    return False
        return True

    for col in range(num_cols - 1):
        for row in range(max_num_rows - 1):
            if does_diag_exist(row, col):
                p1 = grid_position(row, col, web_post_br)
                p2 = grid_position(row+1, col, web_post_tr)
                p3 = grid_position(row+1, col+1, web_post_tl)
                p4 = grid_position(row, col+1, web_post_bl)
                all_connectors.append(hull(p1, p2, p3, p4))

    return union(*all_connectors)

SWITCH_RISER_OFFSET = 9.8 + SWITCH_RISER_RADIUS
switch_riser_offset_square = square_translater_at_offset(SWITCH_RISER_OFFSET)

def get_riser_is_connector(rc1, idx1, rc2, idx2):
    if rc1 == [0, 3] and rc2 == [0, 4]:
        return False
    return True

def get_riser_offset_delta(row_col, idx):
    if row_col == [0, 1] and idx == square_idx_tr:
        return [-2.1, 0]
    if row_col == [0, 3] and idx == square_idx_tl:
        return [2.1, 0]
    if row_col == [0, 3] and idx == square_idx_tr:
        return [0, 0]
    if row_col == [0, 4] and idx == square_idx_tl:
        return [1.5, 0]
    if row_col == [2, 4] and idx == square_idx_bl:
        return [2.9, 0]
    if row_col == [3, 2] and idx == square_idx_br:
        return [-2.9, 0]
    if row_col == [2, 1] and idx == square_idx_br:
        return [-1.5, 0]
    else:
        return None

def wall_connect(row1, col1, idx1, row2, col2, idx2, **kwargs):
    place_fn1 = place_on_grid(row1, col1)
    place_fn2 = place_on_grid(row2, col2)

    delta1 = get_riser_offset_delta([row1, col1], idx1)
    delta2 = get_riser_offset_delta([row2, col2], idx2)

    connectors = get_riser_is_connector([row1, col1], idx1, [row2, col2], idx2)

    return wall_connect_from_placer(place_fn1, idx1, place_fn2, idx2, delta1=delta1, delta2=delta2, connectors=connectors, **kwargs)

def make_offsetter(idx, delta):
    offsetter = get_in_square(switch_riser_offset_square, idx)

    if delta:
        z = 0
        if len(delta) == 3:
            z = delta[2]
        offsetter = translate(delta[0], delta[1], z)(offsetter)
    return offsetter

def wall_connect_from_placer(place_fn1, idx1, place_fn2, idx2, *, delta1=None, delta2=None, connectors=True, walls=True):
    offsetter1 = make_offsetter(idx1, delta1)
    offsetter2 = make_offsetter(idx2, delta2)

    post1 = offsetter1(switch_riser_post)
    post2 = offsetter2(switch_riser_post)

    shapes = []

    if should_include_risers:
        shapes.append(hull(place_fn1(post1), place_fn2(post2)))

    if connectors:
        shapes.append(
            hull(
                place_fn1(union(offsetter1(web_post), get_in_square(web_posts, idx1))),
                place_fn2(union(offsetter2(web_post), get_in_square(web_posts, idx2))),
            )
        )


    if walls:
        shapes.append(
            bottom_hull(hull(
                place_fn1(offsetter1(switch_riser_raw_dot)),
                place_fn2(offsetter2(switch_riser_raw_dot)),
            ))
        )

    return union(*shapes)


def case_walls():
    all_shapes = []

    # Top wall
    for col in range(0, num_cols):
        all_shapes.append(wall_connect(0, col, square_idx_tl, 0, col, square_idx_tr))
    for col in range(0, num_cols - 1):
        all_shapes.append(wall_connect(0, col, square_idx_tr, 0, col + 1, square_idx_tl))

    # Right wall
    max_col = num_cols - 1
    for row in range(0, num_rows_for_col(max_col)):
        all_shapes.append(wall_connect(row, max_col, square_idx_tr, row, max_col, square_idx_br))
    for row in range(0, num_rows_for_col(max_col) - 1):
        all_shapes.append(wall_connect(row, max_col, square_idx_br, row + 1, max_col, square_idx_tr))

    # Left wall
    for row in range(0, num_rows_for_col(0)):
        all_shapes.append(wall_connect(row, 0, square_idx_tl, row, 0, square_idx_bl))
    for row in range(0, num_rows_for_col(0) - 1):
        all_shapes.append(wall_connect(row, 0, square_idx_bl, row + 1, 0, square_idx_tl))

    # Bottom wall
    def include_wall(col):
        return col >= 2

    for col in range(0, num_cols):
        all_shapes.append(wall_connect(num_rows_for_col(col) - 1, col, square_idx_bl, num_rows_for_col(col) - 1, col, square_idx_br, walls=include_wall(col)))
    for col in range(0, num_cols - 1):
        all_shapes.append(wall_connect(num_rows_for_col(col) - 1, col, square_idx_br, num_rows_for_col(col + 1) - 1, col + 1, square_idx_bl, walls=include_wall(col)))

    return union(*all_shapes)

def all_switches():
    return union(*all_of_shape(single_switch))

def filled_switches():
    return union(*all_of_shape(filled_switch))

def all_caps():
    return union(*all_of_shape(sa_cap))

def post_test():
    return union(
        *[y for x in short_web_posts for y in x],
    )

thumb_basic_postition = point_on_grid(num_rows_for_col(1), 1, 0, 0, 0)
thumb_offsets = [15, 7, -5]
# thumb_offsets = [16, 7, -5]
thumb_position = [sum(x) for x in zip(thumb_basic_postition, thumb_offsets)]

def thumb_placer(rot, move):
    return compose(
            rotate_x(rot[0]),
            rotate_y(rot[1]),
            rotate_z(rot[2]),

            translate(*move),

            rotate_z(-10),

            translate(*thumb_position),
    )

thumb_r_placer = thumb_placer([14, -40, 12], [-15.4, -9.8, 5.2])
thumb_m_placer = thumb_placer([10, -23, 20], [-33, -15, -6])
thumb_l_placer = thumb_placer([6, -5, 35], [-52.8, -25.5, -11.5])

thumb_bl_placer = thumb_placer([4, -10, 27], [-33.3, -36.2, -16])
thumb_br_placer = thumb_placer([4, -26, 18], [-13.8, -28.7, -9.6])

thumb_placement_fns = [
    thumb_r_placer,
    thumb_m_placer,
    thumb_l_placer,
    thumb_br_placer,
    thumb_bl_placer,
]

def thumbs_post_offsets(placer, post):
    if placer == thumb_br_placer:
        if post == square_idx_bl:
            return [3, 0, 0]
        if post == square_idx_tr:
            return [0, -3.8, 0]

    if placer == thumb_r_placer:
        if post == square_idx_bl:
            return [11, 0, 0]
        if post == square_idx_tl:
            return [4, 0, 0]

    if placer == thumb_bl_placer:
        if post == square_idx_br:
            return [-3, 0, 0]
        if post == square_idx_tl:
            return [0, -3, 0]

    if placer == thumb_l_placer:
        if post == square_idx_br:
            return [-11.5, 0, 0]

    if placer == thumb_m_placer:
        if post == square_idx_tr:
            return [-2, 0, 0]


    return None

def thumb_wall(place_fn1, idx1, place_fn2, idx2, **kwargs):
    d1 = thumbs_post_offsets(place_fn1, idx1)
    d2 = thumbs_post_offsets(place_fn2, idx2)

    return wall_connect_from_placer(place_fn1, idx1, place_fn2, idx2, delta1=d1, delta2=d2, **kwargs)

def get_offset_thumb_placer(placer, idx, shape):
    delta = thumbs_post_offsets(placer, idx)
    return placer(make_offsetter(idx, delta)(shape))


def thumb_walls():
    return union(
        thumb_wall(thumb_bl_placer, square_idx_bl, thumb_bl_placer, square_idx_br),
        thumb_wall(thumb_bl_placer, square_idx_br, thumb_br_placer, square_idx_bl),
        thumb_wall(thumb_br_placer, square_idx_bl, thumb_br_placer, square_idx_br),

        thumb_wall(thumb_bl_placer, square_idx_bl, thumb_bl_placer, square_idx_tl),

        thumb_wall(thumb_bl_placer, square_idx_tl, thumb_l_placer, square_idx_br, connectors=False),
        thumb_wall(thumb_l_placer, square_idx_br, thumb_l_placer, square_idx_bl, connectors=False),

        thumb_wall(thumb_l_placer, square_idx_bl, thumb_l_placer, square_idx_tl),
        thumb_wall(thumb_l_placer, square_idx_tl, thumb_l_placer, square_idx_tr),

        thumb_wall(thumb_l_placer, square_idx_tr, thumb_m_placer, square_idx_tl),
        thumb_wall(thumb_m_placer, square_idx_tl, thumb_m_placer, square_idx_tr, walls=False),

        thumb_wall(thumb_m_placer, square_idx_tr, thumb_r_placer, square_idx_tl, walls=False),
        thumb_wall(thumb_r_placer, square_idx_tl, thumb_r_placer, square_idx_tr, walls=False),

        thumb_wall(thumb_r_placer, square_idx_tr, thumb_r_placer, square_idx_br, walls=False),

        thumb_wall(thumb_br_placer, square_idx_br, thumb_br_placer, square_idx_tr),

        thumb_wall(thumb_r_placer, square_idx_bl, thumb_r_placer, square_idx_br, walls=False, connectors=False),

        hull(
            get_offset_thumb_placer(thumb_br_placer, square_idx_tr, top_dot),
            get_offset_thumb_placer(thumb_r_placer, square_idx_bl, top_dot),
            get_offset_thumb_placer(thumb_r_placer, square_idx_bl, switch_riser_raw_dot),
        ),

        hull(
            get_offset_thumb_placer(thumb_br_placer, square_idx_tr, top_dot),
            get_offset_thumb_placer(thumb_br_placer, square_idx_tr, switch_riser_raw_dot),
            get_offset_thumb_placer(thumb_r_placer, square_idx_bl, switch_riser_raw_dot),
        ),

        hull(
            get_offset_thumb_placer(thumb_r_placer, square_idx_br, switch_riser_raw_dot),
            get_offset_thumb_placer(thumb_r_placer, square_idx_bl, switch_riser_raw_dot),
            get_offset_thumb_placer(thumb_br_placer, square_idx_tr, switch_riser_raw_dot),
        ),

        bottom_hull(
            hull(
                get_offset_thumb_placer(thumb_r_placer, square_idx_br, switch_riser_raw_dot),
                get_offset_thumb_placer(thumb_br_placer, square_idx_tr, switch_riser_raw_dot),
            )
        ),
    )

def thumb_connectors():
    right_thumb_cover_sphere = get_offset_thumb_placer(thumb_r_placer, square_idx_bl, translate(0, 1.7, 0)(web_post))

    left_thumb_cover_lower_sphere = get_offset_thumb_placer(thumb_bl_placer, square_idx_tl, translate(0, 2, 0)(web_post))
    left_thumb_cover_upper_sphere = thumb_l_placer(translate(0, 0, 0)(web_post_br))

    br_tr_with_offset = thumb_br_placer(translate(0.8, 0.2, 0)(web_post_tr))

    thumb_l_special_point = get_offset_thumb_placer(thumb_l_placer, square_idx_bl, translate(10, 1.1, 0)(web_post))

    return union(
        hull(
            thumb_m_placer(web_post_tr),
            thumb_m_placer(web_post_br),
            thumb_r_placer(web_post_tl),
            thumb_r_placer(web_post_bl),
        ),
        hull(
            thumb_m_placer(web_post_tl),
            thumb_l_placer(web_post_tr),
            thumb_m_placer(web_post_bl),
            thumb_l_placer(web_post_br),
            thumb_m_placer(web_post_bl),
        ),
        hull(
            thumb_bl_placer(web_post_tr),
            thumb_bl_placer(web_post_br),
            thumb_br_placer(web_post_tl),
            thumb_br_placer(web_post_bl),
        ),
        hull(
            thumb_bl_placer(web_post_tl),
            thumb_m_placer(web_post_bl),
            thumb_l_placer(web_post_br),
        ),
        hull(
            thumb_bl_placer(web_post_tl),
            thumb_bl_placer(web_post_tr),
            thumb_m_placer(web_post_bl),
        ),
        hull(
            thumb_bl_placer(web_post_tr),
            thumb_m_placer(web_post_bl),
            thumb_m_placer(web_post_br),
        ),
        hull(
            thumb_br_placer(web_post_tl),
            thumb_bl_placer(web_post_tr),
            thumb_m_placer(web_post_br)
        ),
        hull(
            thumb_m_placer(web_post_br),
            thumb_r_placer(web_post_bl),
            thumb_br_placer(web_post_tl),
        ),
        hull(
            thumb_r_placer(web_post_bl),
            thumb_br_placer(web_post_tl),
            br_tr_with_offset,
        ),

        hull(
            thumb_r_placer(web_post_bl),
            thumb_r_placer(web_post_br),
            br_tr_with_offset,
        ),

        # Right special connectors
        hull(
            right_thumb_cover_sphere,
            get_offset_thumb_placer(thumb_r_placer, square_idx_bl, web_post),
            thumb_r_placer(web_post_br),
            get_offset_thumb_placer(thumb_r_placer, square_idx_br, web_post),
        ),

        hull(
            right_thumb_cover_sphere,
            get_offset_thumb_placer(thumb_r_placer, square_idx_bl, web_post),
            get_offset_thumb_placer(thumb_br_placer, square_idx_tr, switch_riser_raw_dot),
            br_tr_with_offset,
        ),

        # Left special connectors
        hull(
            thumb_l_placer(web_post_bl),
            get_offset_thumb_placer(thumb_l_placer, square_idx_bl, web_post),
            thumb_l_special_point,
        ),

        hull(
            thumb_l_placer(web_post_bl),
            thumb_l_placer(web_post_br),
            thumb_l_special_point,
        ),

        hull(
            left_thumb_cover_lower_sphere,
            get_offset_thumb_placer(thumb_bl_placer, square_idx_tl, web_post),
            thumb_bl_placer(web_post_tl),
        ),

        hull(
            left_thumb_cover_lower_sphere,
            thumb_bl_placer(web_post_tl),
            left_thumb_cover_upper_sphere,
        ),

        hull(
            left_thumb_cover_lower_sphere,
            left_thumb_cover_upper_sphere,
            thumb_l_special_point,
        ),

        hull(
            left_thumb_cover_lower_sphere,
            get_offset_thumb_placer(thumb_l_placer, square_idx_br, web_post),
            thumb_l_special_point,
            get_offset_thumb_placer(thumb_bl_placer, square_idx_tl, web_post),
        ),
    )

def thumb_to_body_connectors():
    return union(
        bottom_hull(
            hull(
                thumb_r_placer(get_in_square(switch_riser_offset_square, square_idx_br)(switch_riser_raw_dot)),
                place_on_grid(3, 2)(get_in_square(switch_riser_offset_square, square_idx_bl)(switch_riser_raw_dot)),
            )
        ),

        hull(
            thumb_r_placer(get_in_square(switch_riser_offset_square, square_idx_br)(switch_riser_raw_dot)),
            thumb_r_placer(get_in_square(switch_riser_offset_square, square_idx_tr)(switch_riser_raw_dot)),
            place_on_grid(3, 2)(get_in_square(switch_riser_offset_square, square_idx_bl)(switch_riser_raw_dot)),
        ),

        hull(
            thumb_r_placer(get_in_square(switch_riser_offset_square, square_idx_tr)(switch_riser_raw_dot)),
            place_on_grid(3, 2)(get_in_square(switch_riser_offset_square, square_idx_bl)(switch_riser_raw_dot)),
            place_on_grid(2, 1)(get_in_square(switch_riser_offset_square, square_idx_br)(switch_riser_raw_dot)),
        ),

        hull(
            thumb_r_placer(get_in_square(switch_riser_offset_square, square_idx_tr)(switch_riser_raw_dot)),
            thumb_r_placer(get_in_square(switch_riser_offset_square, square_idx_tl)(switch_riser_raw_dot)),

            place_on_grid(2, 1)(get_in_square(switch_riser_offset_square, square_idx_br)(switch_riser_raw_dot)),
        ),

        bottom_hull(
            hull(
                thumb_m_placer(get_in_square(switch_riser_offset_square, square_idx_tl)(switch_riser_raw_dot)),
                place_on_grid(2, 0)(get_in_square(switch_riser_offset_square, square_idx_bl)(switch_riser_raw_dot)),
            )
        ),

        hull(
            thumb_m_placer(get_in_square(switch_riser_offset_square, square_idx_tl)(switch_riser_raw_dot)),
            place_on_grid(2, 0)(get_in_square(switch_riser_offset_square, square_idx_bl)(switch_riser_raw_dot)),
            place_on_grid(2, 0)(get_in_square(switch_riser_offset_square, square_idx_br)(switch_riser_raw_dot)),
        ),
    )

def thumb_switches():
    return union(*[fn(single_switch) for fn in thumb_placement_fns])

def filled_thumb_switches():
    return union(*[fn(filled_switch) for fn in thumb_placement_fns])

def bottom_edge_at_position(row, col):
    yield row, col, square_idx_bl
    yield row, col, square_idx_br

def bottom_edge_iterator():
    for col in range(num_cols):
        row = num_rows_for_col(col) - 1

        yield from bottom_edge_at_position(row, col)
    return

def thumb_spots():
    return [
        [thumb_l_placer, square_idx_tl],
        [thumb_l_placer, square_idx_tr],
        [thumb_m_placer, square_idx_tl],
        [thumb_m_placer, square_idx_tr],
        [thumb_r_placer, square_idx_tl],
        [thumb_r_placer, square_idx_tr],
        [thumb_r_placer, square_idx_br],
        [thumb_br_placer, square_idx_br],
    ]

def thumb_caps():
    return union(*[fn(sa_cap) for fn in thumb_placement_fns[-2:]])

def blocker():
    size = 500
    shape = cube(size, size, size)
    shape = translate(-size/2, -size/2, -size)(shape)
    return shape


screw_insert_height = 4.2
screw_insert_bottom_radius = 5.31 / 2.0
screw_insert_top_radius = 5.1 / 2

screw_insert_width = 2
bottom_height = 2

screw_insert_outer = translate(0, 0, bottom_height)(cylinderr1r2(screw_insert_bottom_radius + screw_insert_width, screw_insert_top_radius + screw_insert_width, screw_insert_height + screw_insert_width))
screw_insert_inner = translate(0, 0, bottom_height)(cylinderr1r2(screw_insert_bottom_radius, screw_insert_top_radius, screw_insert_height))

def screw_insert(col, row, shape, ox, oy):
    postiion = point_on_grid(row, col, 0, 0, 0)
    postiion[2] = 0
    postiion[0] += ox
    postiion[1] += oy
    return translate(*postiion)(shape)

def screw_insert_all_shapes(shape):
    return union(
        screw_insert(2, 0, shape, -5.3, 5.9),
        screw_insert(num_cols - 1, 0, shape, 6.7, 5.5),
        screw_insert(num_cols - 1, num_rows_for_col(num_cols - 1), shape, 6.8, 14.4),
        screw_insert(0, 0, shape, -6.2, -6),
        screw_insert(1, max_num_rows + 1, shape, -7.8, 3.4),
        screw_insert(0, max_num_rows - 1, shape, -13.4, 1.7),
    )

trrs_holder_size = [6.0, 11.0, 7.0]
trrs_hole_size = [2.6, 10.0]
trrs_holder_thickness = 2.5

trrs_front_thickness = 1.8

def trrs_key_holder_position():
    base_place = point_on_grid(0, 0, 0, keyswitch_width / 2, 0)
    return [base_place[0] + 3, base_place[1] + 2.43, 8.5]

def trrs_holder():
    shape = cube(
        trrs_holder_size[0] + trrs_holder_thickness,
        trrs_holder_size[1] + trrs_front_thickness,
        trrs_holder_size[2] + trrs_holder_thickness * 2,
    )

    pos = trrs_key_holder_position()

    placed_shape = translate(
            -trrs_holder_size[0] / 2,
            -trrs_holder_size[1],
            -(trrs_holder_size[2] / 2 + trrs_holder_thickness),
    )(shape)

    return translate(*trrs_key_holder_position())(placed_shape)

def trrs_holder_hole():
    rect_hole = cube(*trrs_holder_size)
    rect_hole = translate(
            -trrs_holder_size[0] / 2,
            -trrs_holder_size[1],
            -trrs_holder_size[2] / 2,
        )(rect_hole)

    cylinder_hole = cylinder(*trrs_hole_size, segments=30)
    cylinder_hole = rotate_x(90)(cylinder_hole)
    cylinder_hole = translate(0, 5, 0)(cylinder_hole)

    return translate(*trrs_key_holder_position())(union(rect_hole, cylinder_hole))

usb_holder_hole_dims = [6.5, 15.0, 9.212]
usb_holder_thickness = 2.0

def usb_holder_position():
    base_place = point_on_grid(0, 0, 0, keyswitch_width / 2, 0)
    return [base_place[0] + 13, base_place[1], 9]

def usb_holder_rim():
    base_shape = cube(
        usb_holder_hole_dims[0] + usb_holder_thickness * 2,
        usb_holder_thickness * 2,
        usb_holder_hole_dims[2] + usb_holder_thickness * 2,
    )

    placed_shape = translate(
        -usb_holder_hole_dims[0] / 2 - usb_holder_thickness,
        0,
        -usb_holder_hole_dims[2] / 2 - usb_holder_thickness,
    )(base_shape)

    return translate(*usb_holder_position())(placed_shape)

def usb_holder_hole():
    placed_shape = translate(
        -usb_holder_hole_dims[0] / 2,
        -usb_holder_hole_dims[1] / 2,
        -usb_holder_hole_dims[2] / 2,
    )(cube(*usb_holder_hole_dims))

    return translate(*usb_holder_position())(placed_shape)

reset_switch_hole_height = 4.2
reset_switch_width = 6.0
reset_switch_hole_depth = 6.5
reset_switch_hole_back = 5.0

reset_switch_hole_radius =  4.3 / 2

reset_switch_total_depth = reset_switch_hole_depth + reset_switch_hole_back
reset_switch_total_height = reset_switch_hole_height + 2 * bottom_height

def unplaced_reset_switch_body():
    shape = cube(reset_switch_width, reset_switch_total_depth, reset_switch_total_height, center=True)
    return translate(0, 0, reset_switch_total_height / 2)(shape)

def unplaced_reset_switch_body_hole():
    rect = translate(0, -reset_switch_hole_back / 2.0, reset_switch_hole_height / 2.0 + bottom_height)(
            cube(reset_switch_width + 0.2, reset_switch_hole_depth, reset_switch_hole_height, center=True)
    )
    cyl = translate(0, -reset_switch_hole_back / 2, bottom_height / 2)(cylinder(reset_switch_hole_radius, bottom_height, center=True))

    return union(rect, cyl)

def place_reset_switch_shape(shape):
    base_point = point_on_grid(1, 1, 0, 0, 0)

    return translate(base_point[0], base_point[1], 0)(shape)

reset_switch_body = place_reset_switch_shape(unplaced_reset_switch_body())
reset_switch_body_hole = place_reset_switch_shape(unplaced_reset_switch_body_hole())

def right_shell():
    global should_include_risers
    should_include_risers = True

    cover = translate(-60, 20, 0)(cube(15, 15, 20))

    full_proto = difference(
        union(
            all_switches(),
            connectors(),
            case_walls(),
            screw_insert_all_shapes(screw_insert_outer),
            # all_caps(),

            thumb_switches(),
            thumb_walls(),
            thumb_connectors(),
            # thumb_caps(),
            thumb_to_body_connectors(),

            trrs_holder(),
            usb_holder_rim(),
        ),
        union(
            blocker(),
            screw_insert_all_shapes(screw_insert_inner),
            trrs_holder_hole(),
            usb_holder_hole(),
        ))

    # return intersection(cover, full_proto)
    return full_proto

def left_shell():
    return flip_lr()(right_shell())


screw_head_height = 1.0
screw_head_radius = 5.5 / 2
screw_hole_radius = 1.7

def wall_shape():
    walls_3d = union(
        case_walls(),
        thumb_walls(),
        thumb_to_body_connectors(),
    )

    walls_2d = offset(0.4)(project(cut=True))(translate(0, 0, -0.1)(walls_3d))

    return walls_2d

def model_outline():
    global should_include_risers
    should_include_risers = False

    solid_bottom = project()(union(
        filled_switches(),
        connectors(),
        case_walls(),

        filled_thumb_switches(),
        thumb_walls(),
        thumb_connectors(),

        thumb_to_body_connectors(),
    ))

    bottom_2d = difference(solid_bottom, wall_shape())
    return extrude_linear(bottom_height)(bottom_2d)

weight_width = 19.5
weight_height = 16.5

weight_z_offset = 0.5

def weight_shape():
    return translate(0, 0, 1.5 + weight_z_offset)(cube(weight_width, weight_height, 3, center=True))

def weight_shape_vert():
    return rotate_z(90)(weight_shape())

def place_weight_hole(x, y):
    return translate(x, y, 0)(weight_shape())

def bottom_weight_cutouts():
    shapes = []

    base_point = point_on_grid(0, num_cols - 1, 0, 0, 0)
    base_x = base_point[0] - 9
    base_y = base_point[1] - 4

    space_between = 1
    offsets = space_between + weight_width
    offsets_y = space_between + weight_height

    r3_y = base_y - 2 * offsets_y

    topr = base_y + offsets_y

    for x in range(2):
        shapes.append(place_weight_hole(1 + base_x - offsets * x, base_y))
    for x in range(3, 4):
        shapes.append(place_weight_hole(base_x - offsets * x + 2, base_y))
    for x in range(4, 5):
        shapes.append(place_weight_hole(base_x - offsets * x - 8, base_y))

    for x in range(2, 5):
        shapes.append(place_weight_hole(base_x - offsets * x - 4, base_y - offsets_y))

    for x in range(5):
        shapes.append(place_weight_hole(base_x - offsets * x, base_y - 2 * offsets_y))

    shapes.append(place_weight_hole(base_x - offsets * 2, topr))
    shapes.append(place_weight_hole(base_x - offsets * 3, topr))

    base_thumb_x = base_x - offsets * 4 + 5
    base_thumb_y = base_y - offsets_y * 3 - weight_width + weight_height + 1

    angled_shape = rotate_z(107)(weight_shape())
    shapes.append(translate(base_thumb_x - offsets_y - 0.4, base_thumb_y - 9.5, 0)(angled_shape))
    shapes.append(translate(base_thumb_x - offsets_y + 16, base_thumb_y - 1, 0)(angled_shape))

    return union(*shapes)

reset_switch_body = place_reset_switch_shape(unplaced_reset_switch_body())
reset_switch_body_hole = place_reset_switch_shape(unplaced_reset_switch_body_hole())

def bottom_plate():
    return difference(
            union(
                model_outline(),
                reset_switch_body,
                # screw_insert_all_shapes(screw_insert_outer),
            ),
            union(
                screw_insert_all_shapes(cylinderr1r2(screw_head_radius, screw_head_radius, screw_head_height)),
                screw_insert_all_shapes(cylinderr1r2(screw_hole_radius, screw_hole_radius, bottom_height)),
                bottom_weight_cutouts(),
                reset_switch_body_hole,
            )
        )

def left_bottom_plate():
    return flip_lr()(bottom_plate())

def thumb_corner():
    global should_include_risers
    should_include_risers = True
    return difference(
        union(
            thumb_switches(),
            thumb_walls(),
            thumb_connectors(),
            # thumb_caps(),
            thumb_to_body_connectors(),
        ),
        union(
            blocker(),
        ))

def write_test():
    render_to_file(right_shell(), 'things/right.scad')
    render_to_file(left_shell(), 'things/left.scad')
    render_to_file(bottom_plate(), 'things/right_bottom_plate.scad')
    render_to_file(left_bottom_plate(), 'things/left_bottom_plate.scad')

def run():
    write_test()
    print('done')

if __name__ == '__main__':
    run()
