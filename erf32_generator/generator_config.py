#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import yaml
import logging


class GeneratorConfig:
    """ """

    def __init__(self, config_file):
        """ """
        self.config_file = config_file
        self.clear()
        self.logger = logging.getLogger("erf32_generator")

    def clear(self):
        """ """
        self.ices_config = {}
        # External.
        self.datatype = ""
        self.target_file_template = ""
        self.target_logfile_template = ""
        self.year_from = ""
        self.year_to = ""
        self.source_files = []
        self.taxa_worms_file = ""
        self.translate_files = []
        self.filters_files = []

    def load_config(self):
        """ """
        config_path = pathlib.Path(self.config_file)
        with open(config_path) as file:
            self.ices_config = yaml.load(file, Loader=yaml.FullLoader)

        # "datatype"
        self.datatype = self.ices_config.get("datatype", "")
        # "yearFrom" & "yearTo"
        self.year_from = self.ices_config.get("yearFrom", "")
        self.year_to = self.ices_config.get("yearTo", "")
        # "icesTarget", "fileTemplate", "logFileTemplate"
        target_template, log_template = self.get_target_files()
        self.target_file_template = target_template
        self.target_logfile_template = log_template
        # "sourceFiles"
        self.source_files = self.get_source_file_list()
        # "taxaWorms"
        file_list = self.get_config_files("taxaWorms")
        self.taxa_worms_file = file_list[0]
        # "translate"
        self.translate_files = self.get_config_files("translate")
        # "filters"
        self.filters_files = self.get_config_files("filters")

    def get_target_files(self):
        """ """
        target_path = pathlib.Path()
        log_path = pathlib.Path()
        if "icesTarget" in self.ices_config:
            target_dict = self.ices_config["icesTarget"]
            if "directory" in target_dict:
                target_path = pathlib.Path(target_path, target_dict["directory"])
                log_path = pathlib.Path(log_path, target_dict["directory"])
            if "fileTemplate" in target_dict:
                template = target_dict["fileTemplate"]
                target_path = pathlib.Path(target_path, template)
            if "logfileTemplate" in target_dict:
                log_template = target_dict["logfileTemplate"]
                log_path = pathlib.Path(log_path, log_template)
        return str(target_path), str(log_path)

    def get_source_file_list(self):
        """ """
        source_file_list = []
        file_path = pathlib.Path()
        if "sourceFiles" in self.ices_config:
            source_files = self.ices_config["sourceFiles"]
            if "directory" in source_files:
                directory_path = pathlib.Path(file_path, source_files["directory"])
            if "globSearch" in source_files:
                globSearch = source_files["globSearch"]
                for file_path in pathlib.Path(directory_path).glob(globSearch):
                    if file_path not in source_file_list:
                        source_file_list.append(str(file_path))
            if "files" in source_files:
                for file_name in source_files["files"]:
                    file_path = pathlib.Path(directory_path, file_name)
                    if file_path not in source_file_list:
                        source_file_list.append(str(file_path))
        return sorted(source_file_list)

    def get_config_files(self, config_key):
        """ """
        file_list = []
        file_path = pathlib.Path()
        if config_key in self.ices_config:
            dwca_keys = self.ices_config[config_key]
            if "directory" in dwca_keys:
                dir_path = pathlib.Path(file_path, dwca_keys["directory"])
            if "files" in dwca_keys:
                for file_name in dwca_keys["files"]:
                    file_path = pathlib.Path(dir_path, file_name)
                    file_list.append(str(file_path))
        return file_list

    # def merge_config_yaml_files(self, yaml_file_list):
    #     """ Merge configurations as defined in the yaml file list order. """
    #     result_dict = {}
    #     for file_name in yaml_file_list:
    #         file_path = pathlib.Path(file_name)
    #         with open(file_path, encoding="utf8") as file:
    #             new_data = yaml.load(file, Loader=yaml.FullLoader)
    #             self.dict_deep_update(result_dict, new_data)
    #     # print(result_dict)
    #     return result_dict

    # def dict_deep_update(self, target, updates):
    #     """ Recursively updates or extends a dict. """
    #     for key, value in updates.items():
    #         if value == "REMOVE":
    #             del target[key]
    #         elif isinstance(value, collections.abc.Mapping):
    #             target[key] = self.dict_deep_update(target.get(key, {}), value)
    #         else:
    #             target[key] = value
    #     return target
