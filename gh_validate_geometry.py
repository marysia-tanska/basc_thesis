import settlement.geometry_validator as gv

from ghpythonlib.treehelpers import list_to_tree, tree_to_list

reload(gv)

_sunlight_hours_buildings = tree_to_list(sunlight_hours_buildings, 0)

_sunlight_hours_context = []

geom_validator = gv.GeometryValidator(
    points_in_plot,
    footprints_not_intersecting,
    rotation_modes_check,
    _sunlight_hours_buildings,
    _sunlight_hours_context
)

geometry_is_correct = geom_validator.check_geometry()

if not geometry_is_correct:
    area_score = 0
    average_sunlight_hours_score = 0

else:
    area_score = total_area * (-1)
    average_sunlight_hours_score = geom_validator.get_average_sunlight_hours_per_module() * (-1)
