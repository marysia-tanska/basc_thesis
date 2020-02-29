# constants
MIN_SUNLIGHT_HOURS = 3


class GeometryValidator(object):
    def __init__(
            self,
            points_in_plot,
            footprints_not_intersecting,
            rotation_modes_check,
            sunlight_hours_buildings,
            sunlight_hours_context
    ):
        self.buildings_within_plot = all(points_in_plot)
        self.footprints_not_intersecting = footprints_not_intersecting
        self.rotation_modes_check = rotation_modes_check
        self.sunlight_hours_buildings = sunlight_hours_buildings
        self.sunlight_hours_context = sunlight_hours_context

    def check_floor_types(self):
        for b_index, building in enumerate(self.sunlight_hours_buildings):
            for f_index, floor in enumerate(building):
                modules_check = [m >= MIN_SUNLIGHT_HOURS for m in floor]
                floor_types_dict = {
                    0: (modules_check[0] or modules_check[1] or modules_check[2] or modules_check[3])
                       and (modules_check[4])
                       and (modules_check[5] or modules_check[6] or modules_check[7] or modules_check[8]),

                    1: (modules_check[0] or modules_check[1])
                       and (modules_check[2] or modules_check[3] or modules_check[4])
                       and (modules_check[5] or modules_check[6] or modules_check[7] or modules_check[8]),

                    2: (modules_check[0] or modules_check[2] or modules_check[3])
                       and (modules_check[4] or modules_check[5] or modules_check[6])
                       and (modules_check[7] or modules_check[8]),

                    3: (modules_check[0] or modules_check[1] or modules_check[2] or modules_check[3])
                       and (modules_check[5] or modules_check[6] or modules_check[7] or modules_check[8]),

                    4: (modules_check[0] or modules_check[1] or modules_check[2] or modules_check[3]
                        or modules_check[4])
                       and (modules_check[5] or modules_check[6] or modules_check[7] or modules_check[8]),

                    5: (modules_check[0] or modules_check[1] or modules_check[2] or modules_check[3])
                       and (modules_check[4] or modules_check[5] or modules_check[6] or modules_check[7]
                            or modules_check[8]),

                    6: (modules_check[0] or modules_check[1] or modules_check[2] or modules_check[3])
                       and (modules_check[5] or modules_check[6])
                       and (modules_check[7] or modules_check[8]),

                    7: (modules_check[0] or modules_check[1])
                       and (modules_check[2] or modules_check[3])
                       and (modules_check[5] or modules_check[6] or modules_check[7] or modules_check[8]),
                }
                if not any(floor_types_dict.values()):
                    print b_index, f_index
                    return False
        return True

    def check_sunlight_hours_for_buildings(self):
        return self.check_floor_types()

    def check_sunlight_hours_for_context(self):
        return False

    def get_average_sunlight_hours_per_module(self):
        sunlight_hours = self.sunlight_hours_buildings
        sunlight_hours_per_module_list = [
            _module
            for building in sunlight_hours
            for floor in building
            for _module in floor
        ]
        return sum(sunlight_hours_per_module_list) / float(len(sunlight_hours_per_module_list))

    def check_geometry(self):
        if not self.buildings_within_plot:
            return False
        if not self.footprints_not_intersecting:
            return False
        if not self.rotation_modes_check:
            return False
        if not self.check_sunlight_hours_for_buildings():
            return False
        # if not self.check_sunlight_hours_for_context():
        #     return False
        # if not distances_check_0:
        #     return False
        # if not distances_check_1:
        #     return False
        # if not distances_check_context:
        #     return False
        return True
