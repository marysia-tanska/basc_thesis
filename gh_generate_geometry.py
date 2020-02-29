import rhinoscriptsyntax as rs

import clr
from math import pi
clr.AddReference("RhinoCommon")

import settlement.building_blocks as bb
import settlement.basic_geom as bg

from ghpythonlib.treehelpers import list_to_tree, tree_to_list
from Rhino.Geometry import Line, Mesh, Point2d, Point3d, Polyline, PolylineCurve

reload(bb)
reload(bg)

TEMP_FLOOR_TYPES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']


def get_rhino_mesh(vertices, faces):
    """
    :param vertices: list of Mesh vertices [basic_geom.Point3d]
    :param faces: list of Mesh aces [list of lists of Integers]
    :return: rhino Mesh
    """
    rhino_mesh = Mesh()

    for vertex in vertices:
        rhino_mesh.Vertices.Add(*vertex.coordinates)

    for face in faces:
        rhino_mesh.Faces.AddFace(*face)

    rhino_mesh.Normals.ComputeNormals()
    rhino_mesh.Compact()
    return rhino_mesh


# get building insert point
_insert_points = [bg.Point3d(p.X, p.Y, p.Z) for p in insert_points]

_floor_counts = tree_to_list(floor_counts, 0)
_adding_modes = tree_to_list(adding_modes, 0)

outer_walls_list = []
outer_walls_by_module_list = []
all_floors_outlines = []
floor_meshes_list = []
total_areas = []
rotation_modes_checks = []
footprint_points = []
segment_footprints = []

rotations = [x if x >= 0 else x + (2 * pi) for x in rotations]

for p_index, i_point in enumerate(_insert_points):
    # create buildings
    building = bb.Building(
        i_point,
        rotations[p_index],
        segment_width=bb.SEGMENT_WIDTH,
        segment_depth=bb.SEGMENT_DEPTH,
        regular_floor_height=bb.REGULAR_FLOOR_HEIGHT,
        ground_floor_height=bb.GROUND_FLOOR_HEIGHT,
        last_floor_height=bb.LAST_FLOOR_HEIGHT,
    )

    # calculate floor counts
    building_floor_counts = _floor_counts[p_index]
    building_segments_count = segment_counts[p_index]
    building_adding_modes = [0] + _adding_modes[p_index]
    floor_count = [int(x) for x in building_floor_counts[:building_segments_count]]

    # add building segments
    for s_index in range(building_segments_count):
        building.add_segment(
            adding_mode=building_adding_modes[s_index],
            floor_types=TEMP_FLOOR_TYPES[:building_floor_counts[s_index]]
        )

    first_segment = building.segments[0]

    # calculate footprints
    building_footprint = [
        Polyline([Point3d(*point)
                  for point in segment])
        for segment in building.get_segment_footprints(as_tuples=True)]

    # get floor outlines
    building_floors_outlines = [
        Polyline([Point3d(*point.coordinates)
                  for point in floor_outline.points])
        for segment in building.segments
        for floor_outline in segment.get_floor_and_roof_outlines()
    ]

    all_floors_outlines.append(building_floors_outlines)

    # get floors as a list of rhino Meshes
    building_floor_meshes_list = [
        [
            get_rhino_mesh(
                floor.mesh_vertices, floor.mesh_faces)
            for floor in segment.floors
        ]
        for segment in building.segments]
    floor_meshes_list.append(building_floor_meshes_list)

    # get outer walls as a list of rhino Meshes
    building_outer_walls_list = [
        [
            get_rhino_mesh(
                floor.mesh_vertices, floor.outer_walls_mesh_faces)
            for floor in segment.floors
        ]
        for segment in building.segments]

    # get outer walls by wall module as a list of rhino Meshes for sunlight hours analysis

    building_outer_walls_by_module_list = []

    for segment in building.segments:
        for floor in segment.floors:
            floor_modules_list = []
            floor_vertices, floor_faces = floor.outer_walls_mesh_faces_by_module
            for m_index, module_vertices in enumerate(floor_vertices):
                module_mesh = get_rhino_mesh(module_vertices, floor_faces[m_index])
                floor_modules_list.append(module_mesh)
            building_outer_walls_by_module_list.append(floor_modules_list)

    outer_walls_by_module_list.append(building_outer_walls_by_module_list)
    total_areas.append(building.total_area)
    rotation_modes_checks.append(building.segments_rotation_modes_check)

    # get footprint points and segment footprints
    building_footprint_points = [Point3d(*p.coordinates) for s in building.segments for p in s.footprint_points]
    footprint_points.append(building_footprint_points)

    building_segment_footprints = [
        PolylineCurve([
            Point3d(*p.project_z(0).coordinates)
            for p in s.footprint_points
        ]) for s in building.segments
    ]

    segment_footprints.append(building_segment_footprints)

# convert listes to GH trees
floors_tree = list_to_tree(floor_meshes_list)
floors_tree.SimplifyPaths()

outer_walls_tree = list_to_tree(outer_walls_list)
outer_walls_tree.SimplifyPaths()

outer_walls_by_module_tree = list_to_tree(outer_walls_by_module_list)
outer_walls_by_module_tree.SimplifyPaths()

footprint_points_tree = list_to_tree(footprint_points)
footprint_points_tree.SimplifyPaths()

segment_footprints_tree = list_to_tree(segment_footprints)
segment_footprints_tree.SimplifyPaths()

# calculate total area
total_area = sum(total_areas)

# check rotation modes for the penalty function (if the staircase faces South, return False)
rotation_modes_check = all(rotation_modes_checks)

# get staircase outline
staircase_outline = Polyline([
    Point3d(*point.coordinates)
    for point in building.segments[0].get_staircase_outline().points
])


