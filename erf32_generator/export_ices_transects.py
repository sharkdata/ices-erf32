#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import logging
import erf32_generator


class TransectData(object):
    """ """

    def __init__(self):
        """ """
        self.clear()
        self.logger = logging.getLogger('erf32_generator')

    def clear(self):
        """ """
        self._transect_dict = {}
        self._transect_sequence_no = 0

    def get_transect_data(self, datarow_dict):
        """ """
        # Create key.
        key = self.create_key(datarow_dict)
        #
        if key in self._transect_dict:
            return self._transect_dict[key]
        else:
            return {}

    def get_transect_sequence_no(self, datarow_dict):
        """ """
        # Create key.
        key = self.create_key(datarow_dict)
        #
        if key in self._transect_dict:
            return str(self._transect_dict[key].get("transect_sequence_no", ""))
        else:
            return ""

    def create_key(self, datarow_dict):
        """ """
        key = datarow_dict.get("sample_date", "") + "+"
        key += datarow_dict.get("station_name", "") + "+"
        key += datarow_dict.get("transect_id", "")

        #         key += datarow_dict.get('CruiseIdentifier', '') + '+'
        #         key += datarow_dict.get('StationNumber', '') + '+'
        #         key += datarow_dict.get('Transect', '') + '+'
        key += datarow_dict.get("transect_direction", "") + "+"
        key += datarow_dict.get("transect_start_latitude_dd", "") + "+"
        key += datarow_dict.get("transect_start_longitude_dd", "") + "+"
        key += datarow_dict.get("transect_length_m", "") + "+"
        key += datarow_dict.get("transect_end_latitude_dd", "") + "+"
        key += datarow_dict.get("transect_end_longitude_dd", "") + "+"

        #         key += datarow_dict.get('section_distance_start_m', '') + '+'
        #         key += datarow_dict.get('section_distance_end_m', '') + '+'
        #         key += datarow_dict.get('section_fauna_flora_found', '') + '+'
        #         key += datarow_dict.get('section_start_depth_m', '') + '+'
        #         key += datarow_dict.get('section_end_depth_m', '') + '+'
        #
        #
        #         key += datarow_dict.get('degree_biofouling', '') + '+'
        #         key += datarow_dict.get('bitemark', '') + '+'
        #         key += datarow_dict.get('reproductive_organs', '') + '+'
        #         key += datarow_dict.get('detached', '') + '+'
        #         key += datarow_dict.get('epibiont', '') + '+'
        #         key += datarow_dict.get('stratum_code', '')

        #
        return key

    #         String TransectDirection = sample.getField("sample.transect_direction"); // ICES: TRDGR.
    #         String PositioningSystem = sample.getField("<???>"); // ICES: POSYS.
    #         String TransectStartLatitude = sample.getField("sample.transect_start_latitude_dd"); // ICES: LATRS.
    #         String TransectStartLongitude = sample.getField("sample.transect_start_longitude_dd"); // ICES: LNTRS.
    #         String TransectLength = sample.getField("sample.transect_length"); // ICES: TRSLN.
    #         String TransectEndDetermination = sample.getField("<???>"); // ICES: TREDT.
    #         String TransectEndLatitude = sample.getField("sample.transect_end_latitude_dd"); // ICES: LATRE.
    #         String TransectEndLongitude = sample.getField("sample.transect_end_longitude_dd"); // ICES: LNTRE.
    #         String DepthAdjustment = sample.getField("<???>"); // ICES: DEPAD.
    #         String TransectEndDepth = sample.getField("<???>"); // ICES: TREDP.
    #         String MaxVegetationDepth = sample.getField("<???>"); // ICES: MXVEG.
    #         String SpeciesAtMaxVegetationDepth = sample.getField("<???>"); // ICES: SPVEG.
    #         String RefCodeList = sample.getField("<???>"); // ICES: RLIST.
    #         String DataCentreFlag = sample.getField("<???>"); // ICES: DCFLG.

    # Java.
    # for (Ices40Transect record : recordList) {
    #     if (
    #         record.getCruiseIdentifier().equals(CruiseIdentifier) &&
    #         record.getStationNumber().equals(StationNumber) &&
    #         record.getTransect().equals(Transect) &&
    #         record.getTransectDirection().equals(TransectDirection) && // ICES: TRDGR.
    #         record.getPositioningSystem().equals(PositioningSystem) && // ICES: POSYS.
    #         record.getTransectStartLatitude().equals(TransectStartLatitude) && // ICES: LATRS.
    #         record.getTransectStartLongitude().equals(TransectStartLongitude) && // ICES: LNTRS.
    #         record.getTransectLength().equals(TransectLength) && // ICES: TRSLN.
    #         record.getTransectEndDetermination().equals(TransectEndDetermination) && // ICES: TREDT.
    #         record.getTransectEndLatitude().equals(TransectEndLatitude) && // ICES: LATRE.
    #         record.getTransectEndLongitude().equals(TransectEndLongitude) && // ICES: LNTRE.
    #         record.getDepthAdjustment().equals(DepthAdjustment) && // ICES: DEPAD.
    #         record.getTransectEndDepth().equals(TransectEndDepth) && // ICES: TREDP.
    #         record.getMaxVegetationDepth().equals(MaxVegetationDepth) && // ICES: MXVEG.
    #         record.getSpeciesAtMaxVegetationDepth().equals(SpeciesAtMaxVegetationDepth) && // ICES: SPVEG.
    #         record.getRefCodeList().equals(RefCodeList) && // ICES: RLIST.
    #         record.getDataCentreFlag().equals(DataCentreFlag) ) { // ICES: DCFLG.
    #         return record;
    #     }
    # }
    # Ices40Transect newRecord = new Ices40Transect();

    def load_all_transect_data(self, dataset):
        """ """
        dataheader = dataset.data_header
        for datarow in dataset.data_rows:
            datarow_dict = dict(zip(dataheader, map(str, datarow)))
            # Create key.
            key = self.create_key(datarow_dict)
            if not key in self._transect_dict:
                self._transect_sequence_no += 1
                self._transect_dict[key] = {
                    "transect_sequence_no": str(self._transect_sequence_no)
                }

            #

            transect_length_m = datarow_dict.get("transect_length_m", "")
            if transect_length_m == "":
                #
                max_section_distance_end_m = self._transect_dict[key].get(
                    "max_section_distance_end_m", "0"
                )
                new_section_distance_end_m = datarow_dict.get(
                    "section_distance_end_m", "0"
                )
                #
                try:
                    max_float = float(max_section_distance_end_m.replace(",", "."))
                    if new_section_distance_end_m == "":
                        new_float = 0
                    else:
                        new_float = float(new_section_distance_end_m.replace(",", "."))
                    #
                    if new_float > max_float:
                        self._transect_dict[key]["max_section_distance_end_m"] = str(
                            new_section_distance_end_m
                        ).replace(",", ".")
                except Exception as e:
                    self.logger.error("DEBUG: Transec data exception: " + str(e))
            #
            max_sample_max_depth_m = self._transect_dict[key].get(
                "max_sample_max_depth_m", "0"
            )
            new_sample_max_depth_m = datarow_dict.get("sample_max_depth_m", "0")
            #
            if not max_sample_max_depth_m:
                self._transect_dict[key]["max_sample_max_depth_m"] = str(
                    new_sample_max_depth_m
                ).replace(",", ".")
            #
            if max_sample_max_depth_m and new_sample_max_depth_m:
                try:
                    max_float = float(max_sample_max_depth_m.replace(",", "."))
                    new_float = float(new_sample_max_depth_m.replace(",", "."))
                    #
                    if new_float > max_float:
                        self._transect_dict[key]["max_sample_max_depth_m"] = str(
                            new_sample_max_depth_m
                        ).replace(",", ".")
                except:
                    self.logger.error("DEBUG: Transec data exception: " + str(e))

    def reformat_transect_id(self, transect_id):
        """ """
        if len(transect_id) > 12:
            return transect_id[:5] + ".." + transect_id[-5:]
        else:
            return transect_id

    def stratum_id(self, data_row):
        """ """
        if data_row.get("epibiont", "") == "Y":
            return str(5)
        if data_row.get("detached", "") == "Y":
            return str(6)
        #
        return ""
