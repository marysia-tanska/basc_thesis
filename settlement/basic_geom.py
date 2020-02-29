from math import cos, pi, sin
from copy import deepcopy


# UTILS
def degrees_to_rad(angle):
    return angle / 360. * 2 * pi


def rad_to_degrees(angle):
    return angle / 2. * pi * 360.


class BaseGeom(object):

    pass


class Vector3d(BaseGeom):
    def __init__(self, x, y, z=0.):
        self.x = x
        self.y = y
        self.z = z

    def flip(self):
        self.x = self.x * (-1)
        self.y = self.y * (-1)
        self.z = self.z * (-1)

    @classmethod
    def from_points(cls, point0, point1):
        x = point1.x - point0.x
        y = point1.y - point0.y
        z = point1.z - point0.z
        return cls(x, y, z)


class Point3d(BaseGeom):
    def __init__(self, x, y, z=0.):
        self.x = x
        self.y = y
        self.z = z

    def move(self, vector):
        self.x = self.x + vector.x
        self.y = self.y + vector.y
        self.z = self.z + vector.z

    def move_xyz(self, x, y, z):
        self.x = self.x + x
        self.y = self.y + y
        self.z = self.z + z

    def copy_by_distance_2d(self, distance, angle_2d):
        new_x = self.x + cos(angle_2d) * distance
        new_y = self.y + sin(angle_2d) * distance
        return Point3d(x=new_x, y=new_y, z=self.z)

    def rotate2d(self, centre, angle):
        temp_x = self.x - centre.x
        temp_y = self.y - centre.y
        _x = temp_x * cos(angle) - temp_y * sin(angle)
        _y = temp_y * cos(angle) - temp_x * sin(angle)

        self.x = _x + centre.x
        self.y = _y + centre.y

    @property
    def coordinates(self):
        return self.x, self.y, self.z

    def copy(self, vector=None):
        copied_point = deepcopy(self)
        if vector is not None:
            copied_point.move(vector)
        return copied_point

    def copy_xyz(self, x=0, y=0, z=0):
        copied_point = deepcopy(self)
        copied_point.move_xyz(x, y, z)
        return copied_point

    def project_z(self, z):
        new_point = self.copy()
        new_point.z = z
        return new_point


class Line(BaseGeom):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def flip(self):
        _start = self.start.copy()
        _end = self.end.copy()
        self.start = _end
        self.end = _start

    def to_vector(self):
        return Vector3d.from_points(self.start, self.end)

    @property
    def middle_point(self):
        x = (self.end.x + self.start.x) * 0.5
        y = (self.end.y + self.start.y) * 0.5
        z = (self.end.z + self.start.z) * 0.5

        return Point3d(x, y, z)


class Polyline(BaseGeom):
    def __init__(self, points):
        self.points = points

    def move(self, vector):
        [p.move(vector) for p in self.points]

    def copy_xyz(self, x=0., y=0., z=0.):
        return Polyline([p.copy_xyz(x=x, y=y, z=z) for p in self.points])

    def rotate(self, centre, angle):
        [p.rotate2d(centre, angle) for p in self.points]

    def flip(self):
        self.points = reversed(self.points)

    def copy_and_flip(self):
        return Polyline(reversed(self.points))

    @property
    def points_as_tuples(self):
        return [point.coordinates for point in self.points]

    def to_lines(self):
        return [Line(point, self.points[p_index + 1])
                for p_index, point in enumerate(self.points[:-1])]

    def project_z(self, z):
        return Polyline([p.project_z(z) for p in self.points])

