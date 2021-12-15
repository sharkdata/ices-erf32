#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import zipfile
import logging

import erf32_generator


class Erf32DataShark:
    """Contains a list of all data rows stored as dictionaries.
    Each row doctionary contains fields both for the internal format and DwC.
    """

    def __init__(self, dwca_gen_config):
        """ """
        # Reference to DwcaGenerator object.
        self.dwca_gen_config = dwca_gen_config
        # List of dictionaries containing all data rows.
        self.row_list = []
        # Lookup dictionary for keys to avoid duplicates.
        self.dwc_short_names_exists_dict = {}
        # Field mapping between internal and DwC fields.
        self.dwc_default_mapping = {}
        # # List of keys for dynamic fields.
        # self.used_dynamic_field_key_list = []
        self.logger = logging.getLogger("erf32_generator")

        self.translate = erf32_generator.global_translate

    def get_data_rows(self):
        """ """
        return self.row_list

    def add_shark_dataset(self, dataset_filepath, year_int):
        """Add data from SHARK zipped files."""

        self.logger.info("Adding dataset: " + dataset_filepath)

        # Check if data package is marked for production (PROD).
        status_prod = False
        try:
            with zipfile.ZipFile(dataset_filepath) as z:
                with z.open("processed_data/delivery_note.txt", "r") as f:
                    for row in f:
                        row = row.decode("cp1252")
                        row_items = [str(x.strip()) for x in row.split(":")]
                        if len(row_items) >= 2:
                            key = row_items[0]
                            value = row_items[1]
                            if (key.lower() == "status") and (value.lower() == "prod"):
                                status_prod = True
        except Exception as e:
            self.logger.warning(" - EXCEPTION: failed to read ZIP file: " + str(e))
            self.logger.error(" - EXCEPTION: failed to read ZIP file: " + str(e))
            return

        if not status_prod:
            self.logger.info(" - Package NOT status PROD, skipped: " + dataset_filepath)
            return

        try:
            counter_rows = 0
            counter_filtered = 0
            counter_used = 0
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
                            counter_rows += 1
                            row_dict = dict(zip(header, row_items))

                            # Check visit year. One report for each year.
                            if row_dict.get("visit_year", "") != str(year_int):
                                continue

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
                            ) in erf32_generator.global_filters.get_filters().items():
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

                            # filter_groups = erf32_generator.global_filters.get_filter_include_groups()
                            # for group_key, group_value in filter_groups.items():
                            #     for filter_key, filter_value in group_value.items():
                            #         pass # TODO:

                            filter_groups = (
                                erf32_generator.global_filters.get_filter_exclude_groups()
                            )
                            for group_key, group_value in filter_groups.items():
                                number_of_match = 0
                                for filter_key, filter_value in group_value.items():
                                    value = row_dict.get(filter_key, "")
                                    if str(value) == str(filter_value):
                                        number_of_match += 1
                                if number_of_match == len(group_value):
                                    # msg = row_dict["debug_info"] + "   " + group_key + "   " + str(group_value)
                                    # self.logger.debug(" - Group-exclude: " + msg)
                                    add_row = False

                            # Extra filer. Used for empty values.
                            if add_row:
                                parameter = row_dict.get("parameter", "")
                                if parameter in [
                                    "Sediment redox potential",
                                    "Sediment water content",
                                ]:
                                    value = row_dict.get("value", "")
                                    if value == "":
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
                                counter_used += 1
                                self.row_list.append(row_dict.copy())
                            else:
                                counter_filtered += 1
            #
            msg = (
                " - Rows used: "
                + str(counter_used)
                + "   filtered: "
                + str(counter_filtered)
                + "   total: "
                + str(counter_rows)
            )
            self.logger.info(msg)

        except Exception as e:
            msg = str(dataset_filepath) + str(e)
            self.logger.warning("Exception: " + msg)
