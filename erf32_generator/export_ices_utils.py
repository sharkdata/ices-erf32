#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).


class ExportStations:
    """ """

    def __init__(self):
        """ """
        self.station_info_dict = {}
        self.missing_station_list = []

    def get_mprog(self, station_name):
        """ """
        info_dict = self.get_station_info_dict(station_name)
        mprog = info_dict.get("Station_ProgramGovernance", "")
        ###### mprog = erf32_generator.TranslateValues().get_translated_value('monitoring_program_code', mprog)
        #
        return mprog

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

    def load_export_stations(self, resource_name):
        """ """
        self.station_info_dict = {}
        self.missing_station_list = []
        #
        resource = None
        # try: resource = resources_models.Resources.objects.get(resource_name = resource_name)
        # except ObjectDoesNotExist: resource = None
        #
        if resource:
            data_as_text = resource.file_content  # .encode('cp1252')
            header = []
            for index, row in enumerate(data_as_text.split("\n")):
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
                                print("DEBUG: Stations, duplicate row: " + station_name)


class ExportFilter:
    """ """

    def __init__(self):
        """ """
        self.filter_keep_dict = {}
        self.filter_remove_dict = {}

    def get_filter_keep_list(self, internal_key):
        """ """
        if internal_key in self.filter_keep_dict.keys():
            return self.filter_keep_dict[internal_key]
        else:
            return []

    def get_filter_remove_list(self, internal_key):
        """ """
        if internal_key in self.filter_remove_dict.keys():
            return self.filter_remove_dict[internal_key]
        else:
            return []

    def load_export_filter(self, resource_name):
        """ """
        self.filter_keep_dict = {}
        self.filter_remove_dict = {}
        #
        resource = None
        # try: resource = resources_models.Resources.objects.get(resource_name = resource_name)
        # except ObjectDoesNotExist: resource = None
        #
        if resource:
            data_as_text = resource.file_content  # .encode('cp1252')
            header = []
            for index, row in enumerate(data_as_text.split("\n")):
                row = [item.strip() for item in row.split("\t")]
                if index == 0:
                    header = row
                else:
                    # Keep filter.
                    if len(row) >= 2:
                        internal_key = row[0]
                        keep_value = row[1]
                        if keep_value:
                            if internal_key not in self.filter_keep_dict.keys():
                                self.filter_keep_dict[internal_key] = []
                            #
                            self.filter_keep_dict[internal_key].append(keep_value)
                    # Remove filter.
                    if len(row) >= 3:
                        internal_key = row[0]
                        remove_value = row[2]
                        if remove_value:
                            if internal_key not in self.filter_remove_dict.keys():
                                self.filter_remove_dict[internal_key] = []
                            #
                            self.filter_remove_dict[internal_key].append(remove_value)


class TranslateValues:
    """ """

    def __init__(self):
        """ """
        self.translate_value_dict = {}

    def get_translated_value(self, internal_key, internal_value):
        """ """
        key = internal_key + "<+>" + internal_value
        if key in self.translate_value_dict:
            return self.translate_value_dict[key]
        else:
            return internal_value

    def load_export_translate_values(self, resource_name):
        """ """
        self.translate_value_dict = {}
        #
        resource = None
        # try: resource = resources_models.Resources.objects.get(resource_name = resource_name)
        # except: pass ##### ObjectDoesNotExist: resource = None
        #
        if resource:
            data_as_text = resource.file_content  # .encode('cp1252')
            header = []
            for index, row in enumerate(data_as_text.split("\n")):
                row = [item.strip() for item in row.split("\t")]
                if index == 0:
                    # Supposed to be at least 'internal_key', 'value', 'ices-Erf32'.
                    header = row
                else:
                    if len(row) >= 2:
                        row_dict = dict(zip(header, row))
                        internal_key = row_dict.get("internal_key", "")
                        internal_value = row_dict.get("internal_value", "")
                        ices_export = row_dict.get("ices_export", "")
                        if ices_export:
                            key = internal_key + "<+>" + internal_value
                            self.translate_value_dict[key] = ices_export


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

    def load_translate_taxa(self, resource_name):
        """ """
        self.translate_taxa_dict = {}
        self.missing_taxa_list = []
        #
        resource = None
        # try: resource = resources_models.Resources.objects.get(resource_name = resource_name)
        # except: pass ##### except ObjectDoesNotExist: resource = None
        #
        if resource:
            data_as_text = resource.file_content  # .encode('cp1252')
            header = []
            for index, row in enumerate(data_as_text.split("\n")):
                row = [item.strip() for item in row.split("\t")]
                if index == 0:
                    # Supposed to be at least 'dyntaxa_scientific_name', 'worms_aphia_id', 'ices_rlist'.
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

    def load_translate_taxa(self, resource_name):
        """ """
        self.translate_taxa_dict = {}
        self.missing_taxa_list = []
        #
        resource = None
        # try: resource = resources_models.Resources.objects.get(resource_name = resource_name)
        # except: pass ##### except ObjectDoesNotExist: resource = None
        #
        if resource:
            data_as_text = resource.file_content  # .encode('cp1252')
            header = []
            for index, row in enumerate(data_as_text.split("\n")):
                row = [item.strip() for item in row.split("\t")]
                if index == 0:
                    # Supposed to be at least 'dyntaxa_scientific_name', 'worms_aphia_id', 'ices_rlist'.
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
