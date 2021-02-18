#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import zipfile


class Erf32DataShark:
    """Contains a list of all data rows stored as dictionaries.
    Each row doctionary contains fields both for the internal format and DwC.
    """

    def __init__(self, dwca_gen_config, filters, translate):
        """ """
        # Reference to DwcaGenerator object.
        self.dwca_gen_config = dwca_gen_config
        self.filters = filters
        self.translate = translate
        # List of dictionaries containing all data rows.
        self.row_list = []
        # Lookup dictionary for keys to avoid duplicates.
        self.dwc_short_names_exists_dict = {}
        # Field mapping between internal and DwC fields.
        self.dwc_default_mapping = {}
        # # List of keys for dynamic fields.
        # self.used_dynamic_field_key_list = []

    def get_data_rows(self):
        """ """
        return self.row_list

    def add_shark_dataset(self, dataset_filepath):
        """ Add data from SHARK zipped files. """
        try:
            header = []
            # From file in zip to list of rows.
            with zipfile.ZipFile(dataset_filepath) as z:
                with z.open("shark_data.txt", "r") as f:
                    for index, row in enumerate(f):
                        row = row.decode("cp1252")
                        row_items = [str(x.strip()) for x in row.split("\t")]
                        if index == 0:
                            header = row_items
                        else:
                            row_dict = dict(zip(header, row_items))

                            # Add debug info.
                            dataset_name = row_dict.get("dataset_name", "")
                            if dataset_name:
                                row_dict["debug_info"] = (
                                    "Dataset" + dataset_name + " Row: " + str(index)
                                )

                            # Check filter. Don't add filtered rows.
                            add_row = True
                            for (
                                filter_column_name,
                                filter_dict,
                            ) in self.filters.get_filters().items():
                                value = row_dict.get(filter_column_name, "")
                                if value:
                                    included_values = filter_dict.get(
                                        "included_values", None
                                    )
                                    excluded_values = filter_dict.get(
                                        "excluded_values", None
                                    )
                                    if included_values and (
                                        value not in included_values
                                    ):
                                        add_row = False
                                    if excluded_values and (value in excluded_values):
                                        add_row = False

                            # Check combinations of fields.

                            # filter_groups = self.filters.get_filter_include_groups()
                            # for group_key, group_value in filter_groups.items():
                            #     for filter_key, filter_value in group_value.items():
                            #         pass # TODO:

                            filter_groups = self.filters.get_filter_exclude_groups()
                            for group_key, group_value in filter_groups.items():
                                number_of_match = 0
                                for filter_key, filter_value in group_value.items():
                                    value = row_dict.get(filter_key, "")
                                    if str(value) == str(filter_value):
                                        number_of_match += 1
                                if number_of_match == len(group_value):
                                    print(
                                        "DEBUG: Group-exclude: ",
                                        row_dict["debug_info"],
                                        "   ",
                                        group_key,
                                        "   ",
                                        group_value,
                                    )
                                    add_row = False

                            # Add to list.
                            if add_row:
                                # Translate values.
                                for (
                                    key
                                ) in self.translate.get_translate_from_source_keys():
                                    value = row_dict.get(key, "")
                                    if value:
                                        new_value = (
                                            self.translate.get_translate_from_source(
                                                key, value
                                            )
                                        )
                                        if value != new_value:
                                            row_dict[key] = new_value
                                # Append.
                                self.row_list.append(row_dict.copy())
        except Exception as e:
            print("Exception: ", str(dataset_filepath), e)
