# from abc import ABCMeta, abstractmethod, abstractproperty
from math import ceil, cos, pi, sin
from settlement.basic_geom import Point3d, Polyline


# CONSTANTS (dimensions in cm)
GROUND_FLOOR_HEIGHT = 510.
REGULAR_FLOOR_HEIGHT = 340.
LAST_FLOOR_HEIGHT = 510.

SEGMENT_WIDTH = 1830
SEGMENT_DEPTH = 1260

SEGMENT_AXES_X = 0, 630, 1200, 1830
SEGMENT_AXES_Y = 0, 630, 1260

FlATS_BY_FLOOR_TYPE = {
    'A': [],
    'B': [],
    'C': [],
    'D': [],
    'E': [],
    'F': [],
    'G': [],
    'H': [],
    'I': [],
    'J': [],
    'K': []
}

INCORRECT_ROTATION_MODES = {3, 4, 5}


class Settlement(object):
    def __init__(self, plots, buildings):
        self.plots = plots
        self.buildings = buildings

    def get_score(self):
        return 0.

    def get_daylight_score(self, context):
        return 0.

    def check_distances_in_context(self, context):
        return True

    def check_distances_in_settlement(self):
        return True

    def get_total_area(self):
        return sum([b.get_total_area() for b in self.buildings])


class Building(object):
    def __init__(
            self,
            insert_point,
            rotation,
            segment_width,
            segment_depth,
            regular_floor_height,
            ground_floor_height,
            last_floor_height
    ):
        self.segments = []
        self.insert_point = insert_point
        self.rotation = rotation
        self.segment_width = segment_width
        self.segment_depth = segment_depth
        self.regular_floor_height = regular_floor_height
        self.ground_floor_height = ground_floor_height
        self.last_floor_height = last_floor_height

    @property
    def segments_rotation_modes_check(self):
        return all([s.rotation_mode_check for s in self.segments])

    def add_segment(self, adding_mode, floor_types):
        if self.segments:
            last_segment = self.segments[-1]
            new_segment_insert_point = last_segment.get_new_segment_insert_point(adding_mode=adding_mode)
            last_segment_rotation = last_segment.rotation

        else:
            new_segment_insert_point = self.insert_point
            last_segment_rotation = self.rotation

        if adding_mode in {0, 2}:
            rotation = last_segment_rotation
        elif last_segment_rotation + pi * 0.5 <= 2 * pi:
            rotation = last_segment_rotation + pi * 0.5
        else:
            rotation = last_segment_rotation + pi * 0.5 - 2 * pi

        self.segments.append(
            BuildingSegment(
                self,
                insert_point=new_segment_insert_point,
                rotation=rotation,
                width=self.segment_width,
                depth=self.segment_depth,
                floor_types=floor_types
            ))

    @property
    def total_area(self):
        floors_count = sum([s.floor_count for s in self.segments])
        floor_area = self.segment_width * 0.01 * self.segment_depth * 0.01
        return floors_count * floor_area

    def get_segment_footprints(self, as_tuples=False):
        if not as_tuples:
            return [segment.get_footprint() for segment in self.segments]
        else:
            return [segment.get_footprint().points_as_tuples for segment in self.segments]

    def get_footprint_points(self):
        pass


class BuildingSegment(object):

    def __init__(self, building, insert_point, rotation, width, depth, floor_types, previous_segment=None,
                 next_block=None):
        self.building = building
        self.insert_point = insert_point
        self.rotation = rotation
        self.width = width
        self.depth = depth
        self.floor_count = len(floor_types)
        self.floor_types = floor_types
        self.previous_segment = previous_segment
        self.next_block = next_block

        self.floors = None
        self.grid_points = None

        self.possible_floor_types = None

        self._set_floors()
        self._set_grid_points()

        self._set_possible_floor_types()

        if previous_segment:
            previous_segment.next_segment = self

    def _set_floors(self):
        outline = self.get_footprint()
        z_coordinates = self.get_floors_and_roof_z_coordinates()

        self.floors = [
            Floor(
                building_segment=self,
                outline=outline,
                z1=z1,
                z2=z_coordinates[floor_index + 1],
                floor_type=self.floor_types[floor_index])
            for floor_index, z1 in enumerate(z_coordinates[:-1])]

    def _set_grid_points(self):
        # TODO: dopasowac translacje i rotation

        grid_points = []

        for ax_index, dist_x in enumerate(SEGMENT_AXES_X):
            grid_points.append([])

            temp_point = self.insert_point.copy_by_distance_2d(dist_x, self.rotation)

            for dist_y in SEGMENT_AXES_Y:
                grid_point = temp_point.copy_by_distance_2d(dist_y, self.rotation + 0.5 * pi)
                grid_points[ax_index].append([grid_point.x, grid_point.y, grid_point.z])

        self.grid_points = grid_points

    def _set_possible_floor_types(self):
        # TODO: sprawdzic

        rotation_mode = self.rotation_mode
        possible_floor_types = {
            'A': [2, 2, 2, 0, 0, 0, 1, 2],
            'B': [2, 1, 1, 0, 0, 0, 1, 2],
            'C': [1, 2, 2, 0, 0, 0, 1, 0],
            'D': [2, 2, 2, 0, 0, 0, 2, 2],
            'E': [2, 2, 2, 0, 0, 0, 2, 2],
            'F': [2, 2, 2, 0, 0, 0, 2, 2],
            'G': [1, 2, 2, 0, 0, 0, 1, 0],
            'H': [2, 0, 1, 0, 0, 0, 2, 2],
            'I': [2, 0, 0, 0, 0, 0, 0, 0],
            'J': [2, 0, 0, 0, 0, 0, 0, 0],
            'K': [2, 0, 0, 0, 0, 0, 0, 0]
        }
        return {floor_type: scores[rotation_mode] for floor_type, scores in possible_floor_types.items()}

    def get_height(self):
        return self.building.ground_floor_height\
               + ((self.floor_count - 2) * self.building.regular_floor_height)\
               + self.building.last_floor_height

    def get_rhino_mesh(self):
        vector_x = None
        bottom_points = self.starting_point,
        p2 = self.starting_point.move(self.size_x)
        pass

    def get_flat_types_dict(self):
        return {'A': None,
                'B': None,
                'C': None,
                'D': None,
                'E': None,
                'F': None,
                'G': None,
                'H': None}

    def get_total_area(self):
        return self.size_x * self.size_y * self.floor_count

    @property
    def rotation_mode(self):
        rotation_mode = int((self.rotation + pi / 8.) * 4 / pi)

        return rotation_mode if rotation_mode != 8 else 0

    @property
    def rotation_mode_check(self):
        return self.rotation_mode not in INCORRECT_ROTATION_MODES

    @property
    def footprint_points(self):
        rotation = self.rotation
        point_0 = self.insert_point
        point_1 = point_0.copy_by_distance_2d(self.width, rotation)
        point_2 = point_1.copy_by_distance_2d(self.depth, rotation + pi * 0.5)
        point_3 = point_2.copy_by_distance_2d(self.width, rotation + pi)

        return [point_0, point_1, point_2, point_3, point_0]

    def get_footprint(self):
        point_list = self.footprint_points
        return Polyline(point_list)

    def get_new_segment_insert_point(self, adding_mode=0, new_segment_depth=SEGMENT_DEPTH):

        if adding_mode == 0:
            return Point3d(*self.grid_points[-1][1])

        elif adding_mode == 1:
            return Point3d(*self.grid_points[-1][1]).copy_by_distance_2d(distance=new_segment_depth, angle_2d=self.rotation)

        elif adding_mode == 2:
            return Point3d(*self.grid_points[-1][1]).copy_by_distance_2d(distance=-new_segment_depth, angle_2d=self.rotation + 0.5 * pi)

        elif adding_mode == 3:
            return Point3d(*self.grid_points[-2][-1]).copy_by_distance_2d(distance=new_segment_depth, angle_2d=self.rotation)

        else:
            raise ValueError('Incorrect Segment adding_mode parameter value: {}!'.format(adding_mode))

    def get_floor_outlines(self):
        outlines = []
        footprint = self.get_footprint()
        outlines.append(footprint)
        first_floor_outline = footprint.copy_xyz(z=self.building.ground_floor_height)

        for floor_no in range(0, self.floor_count - 1):
            floor_outline = first_floor_outline.copy_xyz(z=floor_no * self.building.regular_floor_height)
            outlines.append(floor_outline)
        return outlines

    def get_roof_outline(self):
        return self.get_footprint().copy_xyz(z=self.get_height())

    def get_floor_and_roof_outlines(self):
        return self.get_floor_outlines() + [self.get_roof_outline()]

    def get_floors_and_roof_z_coordinates(self):
        ground_floor_height = self.building.ground_floor_height
        regular_floor_height = self.building.regular_floor_height
        insert_z = self.insert_point.z
        z_coordinates = [insert_z]\
                        + [insert_z + ground_floor_height + (regular_floor_height * floor_index)
                           for floor_index in range(self.floor_count - 1)]\
                        + [insert_z + self.get_height()]

        return z_coordinates

    def get_staircase_outline(self):
        gp = self.grid_points
        return Polyline([
            Point3d(*gp[1][1]),
            Point3d(*gp[1][2]),
            Point3d(*gp[2][2]),
            Point3d(*gp[2][1]),
            Point3d(*gp[1][1])]
        )

    def get_staircase_mesh_points(self):
        pass


class Floor(object):
    def __init__(self, building_segment, outline, z1, z2, floor_type):
        self.building_segment = building_segment
        self.z1 = z1
        self.z2 = z2
        self.outline_bottom = outline.project_z(z=z1)
        self.outline_top = outline.project_z(z=z2)
        self.mesh_vertices = None
        self.mesh_faces = None
        self.floor_type = floor_type
        self.flats = []
        self._set_mesh_vertices_and_faces()
        self._set_flats()

    @property
    def grid_points_bottom(self):
        return [[Point3d(*p).project_z(self.z1) for p in grid_axis] for grid_axis in self.building_segment.grid_points]

    @property
    def grid_points_top(self):
        return [[Point3d(*p).project_z(self.z2) for p in grid_axis] for grid_axis in self.building_segment.grid_points]

    @property
    def outer_walls_mesh_faces(self):
        return self.mesh_faces[1:-1]

    @property
    def outer_walls_mesh_faces_by_module(self):
        bottom_pts = self.grid_points_bottom
        top_pts = self.grid_points_top
        modules_vertices = [
            [bottom_pts[0][2], top_pts[0][2], top_pts[1][2], bottom_pts[1][2]],  # 0
            [bottom_pts[0][1], top_pts[0][1], top_pts[0][2], bottom_pts[0][2]],  # 1
            [bottom_pts[0][0], top_pts[0][0], top_pts[0][1], bottom_pts[0][1]],  # 2
            [bottom_pts[1][0], top_pts[1][0], top_pts[0][0], bottom_pts[0][0]],  # 3
            [bottom_pts[2][0], top_pts[2][0], top_pts[1][0], bottom_pts[1][0]],  # 4
            [bottom_pts[3][0], top_pts[3][0], top_pts[2][0], bottom_pts[2][0]],  # 5
            [bottom_pts[3][1], top_pts[3][1], top_pts[3][0], bottom_pts[3][0]],  # 6
            [bottom_pts[3][2], top_pts[3][2], top_pts[3][1], bottom_pts[3][1]],  # 7
            [bottom_pts[2][2], top_pts[2][2], top_pts[3][2], bottom_pts[3][2]],  # 8
        ]
        modules_faces = [[[0, 1, 2, 3]] for _ in modules_vertices]
        return modules_vertices, modules_faces

    def _set_mesh_vertices_and_faces(self):
        bottom_points = self.outline_bottom.points
        top_points = self.outline_top.points
        self.mesh_vertices = bottom_points[:4] + top_points[:4]
        self.mesh_faces = [(0, 3, 2, 1),
                           (0, 1, 5, 4),
                           (1, 2, 6, 5),
                           (2, 3, 7, 6),
                           (3, 0, 4, 7),
                           (4, 5, 6, 7)]

    def _set_flats(self):
        flats_to_set = FlATS_BY_FLOOR_TYPE[self.floor_type]
        self.flats = [flat_class(self, self.z1, self.z2) for flat_class in flats_to_set]


class BaseFlat(object):
    # TODO: dodac podglad mieszkan
    def __init__(self, floor, z1, z2):
        self.floor = floor
        self.outline = self._set_outline(floor.segment.grid_points)
        self.mesh_vertices = []
        self.mesh_faces = []
        self._set_mesh_vertices_and_faces()

    def _set_mesh_vertices_and_faces(self):
        pass


class Flat_0(BaseFlat):
    def _set_outline(self, grid_points):
        self.outline = Polyline([
            Point3d(*grid_points[1][0]),
            Point3d(*grid_points[1][1]),
            Point3d(*grid_points[1][-1]),
            Point3d(*grid_points[0][-1]),
            Point3d(*grid_points[1][0])
        ])


class Flat_1(BaseFlat):
    def _set_outline(self, grid_points):
       self.outline = Polyline([
            Point3d(*grid_points[0][0]),
            Point3d(*grid_points[0][1]),
            Point3d(*grid_points[1][-1]),
            Point3d(*grid_points[0][-1]),
            Point3d(*grid_points[0][0])
        ])