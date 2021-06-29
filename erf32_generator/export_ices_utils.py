#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import logging
import pathlib

import erf32_generator


class ExportStations:
    """ """

    def __init__(self):
        """ """
        self.station_info_dict = {}
        self.missing_station_list = []
        self.logger = logging.getLogger("erf32_generator")
        #
        self.mprog_check = {}

    def get_mprog(self, station_name, default_value=""):
        """ """
        info_dict = self.get_station_info_dict(station_name)
        mprog_used = info_dict.get("Station_ProgramGovernance", default_value)
        mprog_translated = erf32_generator.global_translate.get_translate_from_source(
            "monitoring_program_code", mprog_used
        )
        # Log used alternatives.
        mprog_ices = info_dict.get("Station_ProgramGovernance", "")
        message = (
            "MPROG. Station: "
            + station_name
            + "   SHARK: "
            + default_value
            + "  ICES: "
            + mprog_ices
            + "  Used: "
            + mprog_used
            + "  Translated: "
            + mprog_translated
        )
        if message not in self.mprog_check:
            self.mprog_check[message] = "DUMMY"
            self.logger.info(message)
        #
        return mprog_translated

    def get_wltyp(self, station_name):
        """ """
        info_dict = self.get_station_info_dict(station_name)
        wltyp = info_dict.get("Station_WLTYP", "")
        if wltyp in ["NULL"]:
            return ""
        #
        return wltyp

    def get_mstat(self, station_name):
        """ """
        info_dict = self.get_station_info_dict(station_name)
        mstat = info_dict.get("Station_MSTAT", "")
        if mstat in ["NULL"]:
            return ""
        #
        return mstat

    def get_purpm(self, station_name):
        """ """
        info_dict = self.get_station_info_dict(station_name)
        purpm = info_dict.get("Station_PURPM", "")
        if purpm in ["NULL"]:
            return "E~S~T"
        #
        return purpm

    def get_station_info_dict(self, station_name):
        """ """
        if station_name in self.station_info_dict.keys():
            return self.station_info_dict[station_name]
        #
        if station_name not in self.missing_station_list:
            self.missing_station_list.append(station_name)
        #
        return {}

    def get_missing_station_list(self):
        """ """
        return self.missing_station_list

    def load_export_stations(self):
        """ """
        self.station_info_dict = {}
        self.missing_station_list = []
        #
        station_file_name = "data_in/resources/export_ices_stations_utf8.txt"
        #
        station_file_path = pathlib.Path(station_file_name)
        header = []
        with station_file_path.open("r", encoding="utf8") as file:
            for index, row in enumerate(file):
                row = [item.strip() for item in row.split("\t")]
                if index == 0:
                    header = row
                else:
                    if len(row) >= 2:
                        row_dict = dict(zip(header, map(str, row)))
                        #
                        station_name = str(row_dict.get("Station_Name", ""))
                        if station_name:
                            if station_name not in self.station_info_dict.keys():
                                self.station_info_dict[station_name] = row_dict
                            else:
                                self.logger.warning(
                                    "Stations, duplicate row: " + station_name
                                )


class TranslateTaxa:
    """ """

    def __init__(self):
        """ """
        self.translate_taxa_dict = {}
        self.missing_taxa_list = []

    def get_translated_to_aphiaid(self, scientific_name):
        """ """

        #         if 'Lekanesphaera hookeri' in scientific_name:
        #             print('DEBUG: ' + scientific_name)
        #         if 'Prionospia dubia' in scientific_name:
        #             print('DEBUG: ' + scientific_name)

        if scientific_name in self.translate_taxa_dict:
            return self.translate_taxa_dict[scientific_name]
        #
        if scientific_name not in self.missing_taxa_list:
            self.missing_taxa_list.append(scientific_name)
        #
        return ""

    def get_missing_taxa_list(self):
        """ """
        return self.missing_taxa_list

    def load_translate_taxa(self):
        """ """
        self.translate_taxa_dict = {}
        self.missing_taxa_list = []
        #
        translate_file_name = "data_in/resources/translate_dyntaxa_to_worms.txt"
        #
        translate_file_path = pathlib.Path(translate_file_name)
        header = []
        # with translate_file_path.open("r", encoding="utf8") as file:
        with translate_file_path.open("r", encoding="cp1252") as file:
            for index, row in enumerate(file):
                row = [item.strip() for item in row.split("\t")]
                if index == 0:
                    header = row
                else:
                    if len(row) >= 2:
                        row_dict = dict(zip(header, row))
                        self.translate_taxa_dict[
                            row_dict.get("scientific_name", "")
                        ] = row_dict.get("aphia_id", "")


class TranslateDyntaxaToHelcomPeg:
    """ """

    def __init__(self):
        """ """
        self.translate_taxa_dict = {}

    def get_translated_taxa_and_rlist(self, scientific_name):
        """ """
        if scientific_name in self.translate_taxa_dict:
            return self.translate_taxa_dict[scientific_name]
        #
        return ("", "")

    def load_translate_taxa(self):
        """ """
        self.translate_taxa_dict = {}
        self.missing_taxa_list = []
        #
        translate_file_name = "data_in/resources/translate_dyntaxa_to_helcom_peg.txt"
        #
        translate_file_path = pathlib.Path(translate_file_name)
        header = []
        # with translate_file_path.open("r", encoding="utf8") as file:
        with translate_file_path.open("r", encoding="cp1252") as file:
            for index, row in enumerate(file):
                row = [item.strip() for item in row.split("\t")]
                if index == 0:
                    header = row
                else:
                    if len(row) >= 2:
                        row_dict = dict(zip(header, row))
                        self.translate_taxa_dict[
                            row_dict.get("dyntaxa_scientific_name", "")
                        ] = (
                            row_dict.get("helcom_peg_scientific_name", ""),
                            row_dict.get("ices_rlist", ""),
                        )
