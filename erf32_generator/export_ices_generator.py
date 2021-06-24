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

    def __init__(self, ices_config):
        """ """
        self.ices_config = ices_config
        self.data_rows = []
        self.logger = logging.getLogger("erf32_generator")

    def setup(self, data_rows):
        """ """
        self.data_rows = data_rows

        self.target_file_template = self.ices_config.target_file_template
        self.target_logfile_template = self.ices_config.target_logfile_template

        self.target_file_template = self.target_file_template.replace("<", "")
        self.target_file_template = self.target_file_template.replace(">", "")
        self.target_logfile_template = self.target_logfile_template.replace("<", "")
        self.target_logfile_template = self.target_logfile_template.replace(">", "")

        self.datatype = self.ices_config.datatype
        self.year_from = self.ices_config.year_from
        self.year_to = self.ices_config.year_to
        self.status = ""
        self.user = ""

        self.logfile_name = ""

    def generate_erf32_files(self):
        """ """
        try:
            # Create target directory if not exists.
            target_dir_path = pathlib.Path(self.target_logfile_template).parent
            if not target_dir_path.exists():
                target_dir_path.mkdir(parents=True)
            #
            error_counter = 0
            #
            # Iterate over selected datatypes.
            year_int = int(self.year_from)
            year_to_int = int(self.year_to)
            while year_int <= year_to_int:
                """"""
                self.generate_erf32(
                    self.logfile_name,
                    error_counter,
                    self.datatype,
                    year_int,
                    self.status,
                    self.user,
                )
                #
                year_int += 1
            #
            # Log missing stations.
            # missing_station_list = (
            missing_station_list = (
                erf32_generator.global_export_stations.get_missing_station_list()
            )

            if len(missing_station_list) > 0:
                self.logger.warning("Missing station(s): ")
                for missing_station in sorted(missing_station_list):
                    self.logger.warning("- " + missing_station)
                self.logger.warning("")

            # Log missing taxa.
            missing_taxa_list = (
                erf32_generator.global_translate_taxa.get_missing_taxa_list()
            )
            if len(missing_taxa_list) > 0:
                self.logger.warning("Missing taxa: ")
                for missing_taxa in sorted(missing_taxa_list):
                    self.logger.warning("- " + missing_taxa)

                self.logger.warning("")
            #
            if error_counter > 0:
                self.logger.error("Generation of ICES-Erf32 FAILED")

        except Exception as e:
            error_message = (
                u"Can't generate ICES-Erf32 file." + "\nException: " + str(e) + "\n"
            )
            self.logger.warning(error_message)
            self.logger.warning("FAILED")

    def generate_erf32(self, logfile_name, error_counter, datatype, year, status, user):
        """ """
        # Add all rows from all datasets that match datatype and year.
        erf32_format = erf32_generator.IcesErf32Format()
        #
        try:
            # Phytobentos or Zoobenthos. Transect data for record 40.
            transect_data = erf32_generator.TransectData()
            transect_data.clear()
            if (datatype == "Epibenthos") or \
                (datatype == "Phytobenthos"):
                # transect_data.load_all_transect_data(dataset)
                transect_data.load_all_transect_data(self.data_rows)

            #
            # Process rows.
            for datarow_dict in self.data_rows:
                #
                if datarow_dict.get("visit_year", "") == str(year):

                    # Remove RAMSKRAP.
                    if "FRAMENET" == datarow_dict.get("sampler_type_code", ""):
                        continue

                    # OK to add row.
                    erf32_format.add_row(datarow_dict)

        #
        except Exception as e:
            error_counter += 1
            traceback.print_exc()
            self.logger.error(
                "ERROR: Failed to generate ICES-Erf32." + ".",
            )
        #
        try:
            # Create and save the result.
            out_rows = erf32_format.create_Erf32()
            #
            print("DEBUG: " + str(len(out_rows)))
            #
            if len(out_rows) > 1:
                erf32_format.save_erf32_file(out_rows, str(self.target_file_template))
        #
        except Exception as e:
            error_counter += 1
            traceback.print_exc()
            self.logger.error(
                logfile_name,
                log_row="ERROR: Failed to generate ICES-Erf32 files. Exception: "
                + str(e),
            )
