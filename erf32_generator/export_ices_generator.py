#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import traceback
import datetime
import logging

import erf32_generator


class GenerateIcesErf32(object):
    """ """

    def __init__(self):  # , ices_config):
        """ """
        # self.ices_config = ices_config
        self.data_rows = []
        self.logger = logging.getLogger("erf32_generator")

    def setup(self, data_rows):
        """ """
        self.data_rows = data_rows
        self.status = ""
        self.user = ""
        self.logfile_name = ""

    def generate_erf32(
        self,
        target_file_name,
        logfile_name,
        error_counter,
        datatype,
        status,
        user,
    ):
        """ """
        # Add all rows from all datasets with matching datatype and year.
        erf32_format = erf32_generator.IcesErf32Format()
        #
        try:
            # Phytobentos or Zoobenthos. Transect data for record 40.
            transect_data = erf32_generator.global_transect_data
            transect_data.clear()
            if (datatype == "Epibenthos") or (datatype == "Phytobenthos"):
                # transect_data.load_all_transect_data(dataset)
                transect_data.load_all_transect_data(self.data_rows)

            # Process rows.
            for datarow_dict in self.data_rows:
                # # Remove RAMSKRAP.
                # if "FRAMENET" == datarow_dict.get("sampler_type_code", ""):
                #     continue

                # OK to add row.
                erf32_format.add_row(datarow_dict)

        except Exception as e:
            error_counter += 1
            traceback.print_exc()
            self.logger.error(
                "ERROR: Failed to generate ICES-Erf32." + ".",
            )

        try:
            # Create and save the result.
            out_rows = erf32_format.create_Erf32()
            #
            print("DEBUG: " + str(len(out_rows)))
            #
            if len(out_rows) > 1:
                erf32_format.save_erf32_file(out_rows, target_file_name)

        except Exception as e:
            error_counter += 1
            traceback.print_exc()
            self.logger.error(
                logfile_name,
                log_row="ERROR: Failed to generate ICES-Erf32 files. Exception: "
                + str(e),
            )
