#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import traceback
import datetime

import erf32_generator


class GenerateIcesErf32(object):
    """ """

    def __init__(self, ices_config):
        """ """
        self.ices_config = ices_config
        self.data_rows = []

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
            # Load resource content for ICES station.
            erf32_generator.ExportStations().load_export_stations(
                "export_ices_stations"
            )
            # Load resource content for filtering reported data.
            erf32_generator.ExportFilter().load_export_filter("export_ices_filters")
            # Load resource content to translate values.
            erf32_generator.TranslateValues().load_export_translate_values(
                "export_ices_translate_values"
            )
            # Load resource content to translate from DynTaxa to WoRMS.
            erf32_generator.TranslateTaxa().load_translate_taxa(
                "translate_dyntaxa_to_worms"
            )
            # Load resource content to translate from DynTaxa to Helcom PEG.
            erf32_generator.TranslateDyntaxaToHelcomPeg().load_translate_taxa(
                "translate_dyntaxa_to_helcom_peg"
            )

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
                ""
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
            missing_station_list = (
                erf32_generator.ExportStations().get_missing_station_list()
            )
            if len(missing_station_list) > 0:
                self.target_log_write(self.logfile_name, log_row="Missing station(s): ")
                for missing_station in sorted(missing_station_list):
                    self.target_log_write(
                        self.logfile_name, log_row="- " + missing_station
                    )
                    print("DEBUG: missing station: " + missing_station)
                self.target_log_write(self.logfile_name, log_row="")

            # Log missing taxa.
            missing_taxa_list = erf32_generator.TranslateTaxa().get_missing_taxa_list()
            if len(missing_taxa_list) > 0:
                self.target_log_write(self.logfile_name, log_row="Missing taxa: ")
                for missing_taxa in sorted(missing_taxa_list):
                    # Don't log filtered taxa.
                    if (
                        missing_taxa
                        not in erf32_generator.ExportFilter().get_filter_remove_list(
                            "scientific_name"
                        )
                    ):
                        self.target_log_write(
                            self.logfile_name, log_row="- " + missing_taxa
                        )
                        print("DEBUG: missing taxon: " + missing_taxa)
                self.target_log_write(self.logfile_name, log_row="")
            #
            if error_counter > 0:
                self.target_log_close(self.logfile_name, "FAILED")
            else:
                self.target_log_close(self.logfile_name, "FINISHED")
            #
            print("DEBUG: ICES-Erf32 generation FINISHED")
        except Exception as e:
            self.target_log_write(self.logfile_name, log_row="FAILED")
            error_message = (
                u"Can't generate ICES-Erf32 file." + "\nException: " + str(e) + "\n"
            )
            self.target_log_write(self.logfile_name, log_row=error_message)
            self.target_log_close(self.logfile_name, "FAILED")

    def generate_erf32(self, logfile_name, error_counter, datatype, year, status, user):
        """ """
        # Add all rows from all datasets that match datatype and year.
        erf32_format = erf32_generator.IcesErf32Format()
        #
        #
        # dataset_name = metadata_dict.get("dataset_name", 0)
        # if dataset_name not in erf32_format.ExportFilter().get_filter_keep_list(
        #     "dataset_name"
        # ):
        #     return  # Don't use this dataset.
        #
        try:
            # zip_file_name = db_dataset.dataset_file_name
            # self.target_log_write(
            #     logfile_name,
            #     log_row="Reading archive file: " + zip_file_name + "...",
            # )
            # print("DEBUG: ICES-ZIP processing: " + zip_file_name)
            # #
            # dataset = erf32_format.Dataset()
            # dataset.loadDataFromZipFile(
            #     zip_file_name,
            #     dataset_dir_path=self._ftp_dir_path,
            #     encoding="cp1252",
            # )
            # #
            # dataheader = dataset.data_header
            # print(dataheader)
            # #

            # # Phytobentos or Zoobenthos. Transect data for record 40.
            # transect_data = erf32_format.TransectData()
            # transect_data.clear()
            # if (datatype == "Epibenthos") or \
            #     (datatype == "Phytobenthos"):
            #     transect_data.load_all_transect_data(dataset)

            #
            # Process rows.
            for datarow_dict in self.data_rows:
                #
                if datarow_dict.get("visit_year", "") == str(year):

                    # # Remove some projects.
                    # proj = datarow_dict.get("sample_project_name_en", "")
                    # if not proj:
                    #     proj = datarow_dict.get("sample_project_name_sv", "")
                    # remove_list_sv = (
                    #     erf32_format.ExportFilter().get_filter_remove_list(
                    #         "sample_project_name_sv"
                    #     )
                    # )
                    # remove_list_en = (
                    #     erf32_format.ExportFilter().get_filter_remove_list(
                    #         "sample_project_name_en"
                    #     )
                    # )
                    #
                    # if proj in remove_list_sv:
                    #     continue
                    # if proj in remove_list_en:
                    #     continue

                    # # Remove some stations.
                    # station_name = datarow_dict.get("station_name", "")
                    # if (
                    #     station_name
                    #     in erf32_format.ExportFilter().get_filter_remove_list(
                    #         "station_name"
                    #     )
                    # ):
                    #     continue

                    # # Remove RAMSKRAP.
                    # if "FRAMENET" == datarow_dict.get("sampler_type_code", ""):
                    #     continue

                    # OK to add row.
                    erf32_format.add_row(datarow_dict)

        #
        except Exception as e:
            error_counter += 1
            traceback.print_exc()
            self.target_log_write(
                logfile_name,
                log_row="ERROR: Failed to generate ICES-Erf32 from: "
                # + zip_file_name
                + ".",
            )
        #
        try:
            # Create and save the result.
            out_rows = erf32_format.create_Erf32()
            #
            print("DEBUG: " + str(len(out_rows)))
            #
            if len(out_rows) > 1:
                #
                # export_name = "ICES-Erf32" + "_SMHI_" + datatype + "_" + str(year)
                # export_file_name = export_name + ".Erf32"
                # export_file_path = pathlib.Path(self._export_dir_path, export_file_name)
                # error_log_file = export_name + "_log.txt"
                # error_log_file_path = pathlib.Path(
                #     self._export_dir_path, error_log_file
                # )
                #
                # erf32_format.save_erf32_file(out_rows, str(export_file_path))
                erf32_format.save_erf32_file(out_rows, str(self.target_file_template))

                # Log file.
                log_rows = []
                log_rows.append("")
                log_rows.append("")
                log_rows.append(
                    "Generate ICES-Erf32 files. " + str(datetime.datetime.now())
                )
                log_rows.append("")
                # log_rows.append("- Format: " + dbrow.format)
                log_rows.append("- Datatype: " + str(datatype))
                log_rows.append("- Year: " + str(year))
                # log_rows.append("- Status: " + str(dbrow.status))
                # log_rows.append("- Approved: " + str(dbrow.approved))
                # log_rows.append("- Export name: " + str(dbrow.export_name))
                log_rows.append("- Export file name: " + str(self.target_file_template))
                log_rows.append("")
                #
                # erf32_format.save_log_file(log_rows, str(error_log_file_path))
                erf32_format.save_log_file(log_rows, str(self.target_logfile_template))
        #
        except Exception as e:
            error_counter += 1
            traceback.print_exc()
            self.target_log_write(
                logfile_name,
                log_row="ERROR: Failed to generate ICES-Erf32 files. Exception: "
                + str(e),
            )

    def target_log_write(self, logfile_name, log_row=""):
        """ """
        print("LOGGER-TODO: ", log_row)

    def target_log_close(self, logfile_name, status=""):
        """ """
        print("LOGGER-TODO: CLOSED: ", status)