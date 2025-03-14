import numpy as np
import cv2
import math

def map_to_bottom_left(x, y, width, height):
    """Convert model coordinate (x,y), origin at bottom-left, 
    to image coordinate (x,y) in OpenCV, origin at top-left."""
    return (x, height - y)

def is_in_rectangle(x, y, x_min, x_max, y_min, y_max):
    return (x_min <= x <= x_max) and (y_min <= y <= y_max)

def is_in_polygon(x, y, polygon):
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i+1) % n]
        if ((y1 > y) != (y2 > y)):
            x_intersect = x1 + (y - y1)*(x2 - x1)/(y2 - y1)
            if x_intersect > x:
                inside = not inside
    return inside

def is_in_circle(x, y, cx, cy, r):
    return (x - cx)**2 + (y - cy)**2 <= r*r

def is_in_ellipse_filled(x, y, cx, cy, rx, ry, angle_deg, start_deg, end_deg):
    dx = x - cx
    dy = y - cy
    theta = -math.radians(angle_deg)
    cosT = math.cos(theta)
    sinT = math.sin(theta)
    x_ell = dx*cosT - dy*sinT
    y_ell = dx*sinT + dy*cosT
    if (x_ell**2)/(rx*rx) + (y_ell**2)/(ry*ry) > 1.0:
        return False
    ang = math.degrees(math.atan2(y_ell, x_ell))
    if ang < 0:
        ang += 360
    s = start_deg % 360
    e = end_deg % 360
    if s <= e:
        return s <= ang <= e
    else:
        return (ang >= s) or (ang <= e)

# The letter/digit obstacles: E, N, P, M, 6, 1 (no clearance)
def is_in_E(x, y):
    r1 = is_in_rectangle(x, y, 50, 70, 60, 240)
    r2 = is_in_rectangle(x, y, 70, 130, 220, 240)
    r3 = is_in_rectangle(x, y, 70, 110, 140, 160)
    r4 = is_in_rectangle(x, y, 70, 130, 60, 80)
    return r1 or r2 or r3 or r4

def is_in_N(x, y):
    r1 = is_in_rectangle(x, y, 200, 220, 60, 240)
    r2 = is_in_rectangle(x, y, 280, 300, 60, 240)
    diag_poly = [(290,60), (270,60), (210,240), (230,240)]
    diag = is_in_polygon(x, y, diag_poly)
    return r1 or r2 or diag

def is_in_P(x, y):
    rect_p = is_in_rectangle(x, y, 350, 370, 60, 240)
    ell_p  = is_in_ellipse_filled(x, y, 370, 200, 40, 40, 0, -90, 90)
    return rect_p or ell_p

def is_in_M(x, y):
    r1 = is_in_rectangle(x, y, 460, 480, 60, 240)
    r2 = is_in_rectangle(x, y, 580, 600, 60, 240)
    left_diag = [(470,240),(490,240),(540,60),(520,60)]
    ld = is_in_polygon(x, y, left_diag)
    right_diag= [(540,60),(520,60),(570,240),(590,240)]
    rd = is_in_polygon(x, y, right_diag)
    return r1 or r2 or ld or rd

def is_in_6_first(x, y):
    bottom_circle = is_in_circle(x, y, 695, 105, 50)
    radius_top_arc = 150
    center_top_arc = (795, 105)
    rect_size = 10
    top_arc_hit = False
    for deg in range(120, 181):
        rad = math.radians(deg)
        px = center_top_arc[0] + radius_top_arc * math.cos(rad)
        py = center_top_arc[1] + radius_top_arc * math.sin(rad)
        x_min = px - rect_size/2
        x_max = px + rect_size/2
        y_min = py - rect_size/2
        y_max = py + rect_size/2
        if (x_min <= x <= x_max) and (y_min <= y <= y_max):
            top_arc_hit = True
            break
    return (bottom_circle or top_arc_hit)

def is_in_6_second(x, y):
    bottom_circle = is_in_circle(x, y, 845, 105, 50)
    radius_top_arc = 150
    center_top_arc = (945, 105)
    rect_size = 10
    top_arc_hit = False
    for deg in range(120, 180):
        rad = math.radians(deg)
        px = center_top_arc[0] + radius_top_arc * math.cos(rad)
        py = center_top_arc[1] + radius_top_arc * math.sin(rad)
        x_min = px - rect_size/2
        x_max = px + rect_size/2
        y_min = py - rect_size/2
        y_max = py + rect_size/2
        if (x_min <= x <= x_max) and (y_min <= y <= y_max):
            top_arc_hit = True
            break
    return (bottom_circle or top_arc_hit)

def is_in_1(x, y):
    return is_in_rectangle(x, y, 950, 970, 60, 240)

def is_obstacle(x, y):
    """Check if (x,y) falls into any letter/digit obstacle."""
    return (is_in_E(x, y) or
            is_in_N(x, y) or
            is_in_P(x, y) or
            is_in_M(x, y) or
            is_in_6_first(x, y) or
            is_in_6_second(x, y) or
            is_in_1(x, y))


def main():
    width, height = 1000, 300
    obstacle_map = np.ones((height, width, 3), dtype=np.uint8)*255

    
    for py in range(height):
        for px in range(width):
            y_model = height - 1 - py
            if is_obstacle(px, y_model):
                obstacle_map[py, px] = (0, 0, 0)
    cv2.imshow("Obstacle Space: ENPM661 (Half-planes & Semi-algebraic)", obstacle_map)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
