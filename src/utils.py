import math


def distance(point_a, point_b):
    return math.hypot(point_a[0] - point_b[0], point_a[1] - point_b[1])


def midpoint(point_a, point_b):
    return int((point_a[0] + point_b[0]) / 2), int((point_a[1] + point_b[1]) / 2)


def angle_degrees(point_a, point_b, point_c):
    vector_ab = (point_a[0] - point_b[0], point_a[1] - point_b[1])
    vector_cb = (point_c[0] - point_b[0], point_c[1] - point_b[1])
    dot = vector_ab[0] * vector_cb[0] + vector_ab[1] * vector_cb[1]
    length_ab = math.hypot(*vector_ab)
    length_cb = math.hypot(*vector_cb)
    if length_ab == 0 or length_cb == 0:
        return 0
    cosine = max(-1, min(1, dot / (length_ab * length_cb)))
    return math.degrees(math.acos(cosine))


def smooth_value(previous, current, alpha):
    if previous is None:
        return current
    return previous + (current - previous) * alpha


def smooth_point(previous, current, alpha):
    if previous is None:
        return current
    return (
        int(smooth_value(previous[0], current[0], alpha)),
        int(smooth_value(previous[1], current[1], alpha)),
    )


def smooth_rect(previous, current, alpha):
    if previous is None:
        return current
    return tuple(int(smooth_value(prev_value, curr_value, alpha)) for prev_value, curr_value in zip(previous, current))


def clamp_rect(rect, frame_shape):
    frame_height, frame_width = frame_shape[:2]
    x1, y1, x2, y2 = rect
    x1 = max(0, min(frame_width - 1, x1))
    y1 = max(0, min(frame_height - 1, y1))
    x2 = max(0, min(frame_width, x2))
    y2 = max(0, min(frame_height, y2))
    return x1, y1, x2, y2


def point_in_rect(point, rect):
    if point is None:
        return False
    x, y = point
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2
