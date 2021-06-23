#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import codecs
import logging
import erf32_generator


class IcesErf32Format(object):
    """ """

    def __init__(self):
        """ """
        self.datarow_dict = {}
        self._rec20_dict = {}
        self._rec21_dict = {}
        self._zp_abundnr_wetwt_list = []
        #
        self.logger = logging.getLogger('erf32_generator')
        #
        self._duplicate_counter = 0
        self._34rec_counter = 0
        # # Load resource file containing WoRMS info for taxa.
        # self.worms_info_object = erf32_generator.SpeciesWormsInfo()
        # self.worms_info_object.loadSpeciesFromResource()
        #
        self.define_fields_and_keys()

    def add_row(
        self,
        datarow_dict,
    ):
        """ """
        # Check if parameter should be reported.
        row_parameter = datarow_dict["parameter"]
        row_unit = datarow_dict["unit"]
        if row_parameter in self.filter_parameters:

            # Special for ZP.
            if (row_parameter == "Carbon content") and (row_unit != "ug/m3"):
                return

            #
            ices_content = erf32_generator.ExportIcesContent(datarow_dict)
            ices_content.copy_to_ices_fields()

            ices_content.cleanup_ices_fields()

            ices_content.add_transect_fields()

            ices_content.add_rec20(self._rec20_dict, self.rec20_fields)
            ices_content.add_rec21(self._rec21_dict, self.rec21_fields)
            #
            key38 = self.add_key_strings(datarow_dict)
            if key38 in self.datarow_dict:
                # Aggregate over dev_stage_code if ZP.
                if (datarow_dict["DTYPE-R34"] == "ZP") and (
                    datarow_dict["STAGE-R38"] in ["C1", "C2", "C3", "C4", "C5"]
                ):
                    try:
                        old_datarow_dict = self.datarow_dict[key38]
                        old_value = float(old_datarow_dict.get("VALUE-R38", "0"))
                        new_value = float(datarow_dict.get("VALUE-R38", "0"))
                        aggregated_value = old_value + new_value
                        datarow_dict["VALUE-R38"] = "{0:f}".format(
                            aggregated_value
                        )  # .rename(',', '.')
                    except:
                        self.logger.error("DEBUG: Failed to aggregate ZP values.")
                else:
                    self._duplicate_counter += 1
                    self.logger.warning(
                        "Duplicate found ("
                        + str(self._duplicate_counter)
                        + "): "
                        + key38
                    )
            #
            self.datarow_dict[key38] = datarow_dict

            # ZP must have both ABUNDNR and WETWT.
            ices_content.check_zp_abundnr_wetwt(
                self.datarow_dict, self._zp_abundnr_wetwt_list
            )

    def create_Erf32(self):
        """ """
        # if settings.DEBUG: print('DEBUG: Number of rows: ' + str(len(self.datarow_dict.keys())))
        #
        out_rows = []
        # Erf32 header.
        out_rows.append('<?xml version="1.0" encoding="ISO-8859-1" ?>')
        # Erf32 elements.
        rec00_element = False
        rec90_element = False
        rec91_element = False
        rec40_element = False
        rec34_element = False
        rec38_element = False
        rec90_lastusedkey = "first"
        rec91_lastusedkey = "first"
        rec40_lastusedkey = "first"
        rec34_lastusedkey = "first"
        rec38_lastusedkey = "first"
        # Iterate over rows. Important note: Sorted by the keys_r38 key.
        for rowdictkey in sorted(self.datarow_dict.keys()):
            rowdict = self.datarow_dict[rowdictkey]
            #             if settings.DEBUG: print('DEBUG: Row as dict: ' + str(rowdict))

            #             if rowdict.get("SMPNO-R34", "") == "51d548f222eeb16ea91800d8f23ef405":
            #                 print("DEBUG")

            # ===== Rec 00. =====
            if rec00_element == False:
                rec00_element = True
                out_rows.append("<R00.FileInformation>")
                #
                for field in self.rec00_fields:
                    if rowdict.get(field, False):
                        field_ices = field.split("-R")[0]
                        out_rows.append(
                            "  <"
                            + field_ices
                            + ">"
                            + rowdict.get(field, "")
                            + "</"
                            + field_ices
                            + ">"
                        )

            # ===== Rec 90. =====
            if rec90_lastusedkey != rowdict.get("rec90_key", ""):
                # Close old.
                if rec38_element == True:
                    out_rows.append("          </R38.BiologicalCommunityAbundance>")
                if rec34_element == True:
                    out_rows.append("        </R34.BiologicalCommunitySample>")
                if rec40_element == True:
                    out_rows.append("      </R40.TransectDescription>")
                if rec91_element == True:
                    out_rows.append("    </R91.SamplingEventRecord>")
                if rec90_element == True:
                    out_rows.append("  </R90.SamplingPlatformRecord>")
                rec38_element = False
                rec34_element = False
                rec40_element = False
                rec91_element = False
                # Open new.
                rec90_element = True
                rec90_lastusedkey = rowdict.get("rec90_key", "")
                out_rows.append("  <R90.SamplingPlatformRecord>")
                #
                for field in self.rec90_fields:
                    if rowdict.get(field, False):
                        field_ices = field.split("-R")[0]
                        out_rows.append(
                            "    <"
                            + field_ices
                            + ">"
                            + rowdict.get(field, "")
                            + "</"
                            + field_ices
                            + ">"
                        )

            # ===== Rec 91. =====
            if rec91_lastusedkey != rowdict.get("rec91_key", ""):
                # Close old.
                if rec38_element == True:
                    out_rows.append("          </R38.BiologicalCommunityAbundance>")
                if rec34_element == True:
                    out_rows.append("        </R34.BiologicalCommunitySample>")
                if rec40_element == True:
                    out_rows.append("      </R40.TransectDescription>")
                if rec91_element == True:
                    out_rows.append("    </R91.SamplingEventRecord>")
                rec38_element = False
                rec34_element = False
                rec40_element = False
                # Open new.
                rec91_element = True
                rec91_lastusedkey = rowdict.get("rec91_key", "")
                out_rows.append("    <R91.SamplingEventRecord>")
                #
                for field in self.rec91_fields:
                    if rowdict.get(field, False):
                        field_ices = field.split("-R")[0]
                        out_rows.append(
                            "      <"
                            + field_ices
                            + ">"
                            + rowdict.get(field, "")
                            + "</"
                            + field_ices
                            + ">"
                        )

            # ===== Rec 40. =====
            # Rec 40 used for Phytobenthos. (Valid for Zoobentos if transects are used, but thats not the case for SMHI.)
            if rowdict.get("DTYPE-R34", "") == "PB":
                if rec40_lastusedkey != rowdict.get("rec40_key", ""):
                    # Close old.
                    if rec38_element == True:
                        out_rows.append("          </R38.BiologicalCommunityAbundance>")
                    if rec34_element == True:
                        out_rows.append("        </R34.BiologicalCommunitySample>")
                    if rec40_element == True:
                        out_rows.append("      </R40.TransectDescription>")
                    rec38_element = False
                    rec34_element = False
                    # Open new.
                    rec40_element = True
                    rec40_lastusedkey = rowdict.get("rec40_key", "")
                    out_rows.append("      <R40.TransectDescription>")
                    #
                    for field in self.rec40_fields:
                        if rowdict.get(field, False):
                            field_ices = field.split("-R")[0]
                            out_rows.append(
                                "        <"
                                + field_ices
                                + ">"
                                + rowdict.get(field, "")
                                + "</"
                                + field_ices
                                + ">"
                            )

            # ===== Rec 34. =====
            if rec34_lastusedkey != rowdict.get("rec34_key", ""):
                # Close old.
                if rec38_element == True:
                    out_rows.append("          </R38.BiologicalCommunityAbundance>")
                if rec34_element == True:
                    out_rows.append("        </R34.BiologicalCommunitySample>")
                rec38_element = False
                rec34_element = False
                # Open new.
                rec34_element = True
                rec34_lastusedkey = rowdict.get("rec34_key", "")
                out_rows.append("        <R34.BiologicalCommunitySample>")
                #
                if rowdict.get("SMPNO-R34", "").startswith("9999"):
                    self._34rec_counter += 1
                    rowdict["SMPNO-R34"] = (
                        rowdict["SMPNO-R34"] + "-" + str(self._34rec_counter)
                    )
                #
                for field in self.rec34_fields:
                    if rowdict.get(field, False):
                        field_ices = field.split("-R")[0]
                        out_rows.append(
                            "          <"
                            + field_ices
                            + ">"
                            + rowdict.get(field, "")
                            + "</"
                            + field_ices
                            + ">"
                        )

            # ===== Rec 38. =====
            remove_value = False
            # Some species are filtered.
            if "<REMOVE>" in rowdict.get("SPECI-R38", ""):
                remove_value = True
                self.logger.warning("DEBUG: <REMOVE>" + rowdict.get("scientific_name", ""))

            #             # ZP must have both ABUNDNR and WETWT.
            #             elif rowdict['DTYPE-R34'] == 'ZP':
            #                 param = rowdict['PARAM-R38']
            #                 if param in ['ABUNDNR', 'BMWETWT', ]:
            #                     rec38_key = rowdict['rec38_key']
            #                     if param == 'ABUNDNR':
            #                         new_key = rec38_key.replace('ABUNDNR+nr', 'BMWETWT+g')
            #                         if new_key in self._zp_abundnr_wetwt_list:
            #                             remove_value = False
            #                         else:
            #                             remove_value = True
            #                     elif param == 'BMWETWT':
            #                         new_key = rec38_key.replace('BMWETWT+g', 'ABUNDNR+nr')
            #                         if new_key in self._zp_abundnr_wetwt_list:
            #                             remove_value = False
            #                         else:
            #                             remove_value = True

            #
            if not remove_value:
                if rec38_lastusedkey != rowdict.get("rec38_key", ""):
                    # Close old.
                    if rec38_element == True:
                        out_rows.append("          </R38.BiologicalCommunityAbundance>")
                    # Open new.
                    rec38_element = True
                    rec38_lastusedkey = rowdict.get("rec38_key", "")
                    out_rows.append("          <R38.BiologicalCommunityAbundance>")
                    #
                    for field in self.rec38_fields:
                        if rowdict.get(field, False):
                            field_ices = field.split("-R")[0]
                            out_rows.append(
                                "            <"
                                + field_ices
                                + ">"
                                + rowdict.get(field, "")
                                + "</"
                                + field_ices
                                + ">"
                            )
        #
        if rec38_element:
            out_rows.append("          </R38.BiologicalCommunityAbundance>")
        if rec34_element:
            out_rows.append("        </R34.BiologicalCommunitySample>")
        if rec40_element:
            out_rows.append("      </R40.TransectDescription>")
        if rec91_element:
            out_rows.append("    </R91.SamplingEventRecord>")
        if rec90_element:
            out_rows.append("  </R90.SamplingPlatformRecord>")
        #
        if len(self._rec20_dict) > 0:
            for key in self._rec20_dict.keys():
                out_rows.append("  <R20.SamplingMethod>")
                r20_dict = self._rec20_dict[key]
                r20_dict["SMLNK-R20"] = r20_dict["sequence_number"]
                for field in self.rec20_fields:
                    if r20_dict.get(field, False):
                        field_ices = field.split("-R")[0]
                        out_rows.append(
                            "    <"
                            + field_ices
                            + ">"
                            + r20_dict.get(field, "")
                            + "</"
                            + field_ices
                            + ">"
                        )
                out_rows.append("  </R20.SamplingMethod>")
        #
        if len(self._rec21_dict) > 0:
            for key in self._rec21_dict.keys():
                out_rows.append("  <R21.AnalyticalMethod>")
                r21_dict = self._rec21_dict[key]
                r21_dict["AMLNK-R21"] = r21_dict["sequence_number"]
                for field in self.rec21_fields:
                    if r21_dict.get(field, False):
                        field_ices = field.split("-R")[0]
                        out_rows.append(
                            "    <"
                            + field_ices
                            + ">"
                            + r21_dict.get(field, "")
                            + "</"
                            + field_ices
                            + ">"
                        )
                out_rows.append("  </R21.AnalyticalMethod>")
        #
        if rec00_element:
            out_rows.append("</R00.FileInformation>")
        #
        # Replace all "," with ".".
        for index, row in enumerate(out_rows):
            if "," in row:
                self.logger.debug('DEBUG: "," found in row: ', row)
                out_rows[index] = row.replace(",", ".")

        return out_rows

    def save_erf32_file(
        self, out_rows, file_path_name, encoding="cp1252", row_separator="\r\n"
    ):
        """ """
        outfile = None
        try:
            outfile = codecs.open(file_path_name, mode="w", encoding=encoding)
            for row in out_rows:
                outfile.write(row + row_separator)
        except (IOError, OSError):
            raise UserWarning("Failed to write Erf32 file: " + file_path_name)
        finally:
            if outfile:
                outfile.close()

    def save_log_file(
        self, out_rows, file_path_name, encoding="cp1252", row_separator="\r\n"
    ):
        """ """
        outfile = None
        try:
            outfile = codecs.open(file_path_name, mode="w", encoding=encoding)
            for row in out_rows:
                outfile.write(row + row_separator)
        except (IOError, OSError):
            raise UserWarning("Failed to write log file: " + file_path_name)
        finally:
            if outfile:
                outfile.close()

    def add_key_strings(self, row_dict):
        """ Adds all needed keys to the dictionary. Returns key for the row. """
        # Create key values.
        rec00_key = self.create_key_string(row_dict, self.rec00_keys)
        rec90_key = self.create_key_string(row_dict, self.rec90_keys)
        rec91_key = self.create_key_string(row_dict, self.rec91_keys)
        rec40_key = self.create_key_string(row_dict, self.rec40_keys)
        rec34_key = self.create_key_string(row_dict, self.rec34_keys)
        rec38_key = self.create_key_string(row_dict, self.rec38_keys)
        rec20_key = self.create_key_string(row_dict, self.rec20_keys)
        rec21_key = self.create_key_string(row_dict, self.rec21_keys)
        rec94_key = self.create_key_string(row_dict, self.rec94_keys)
        # Add keys to dict.
        row_dict["rec00_key"] = rec00_key
        row_dict["rec90_key"] = rec90_key
        row_dict["rec91_key"] = rec91_key
        row_dict["rec40_key"] = rec40_key
        row_dict["rec34_key"] = rec34_key
        row_dict["rec38_key"] = rec38_key
        row_dict["rec20_key"] = rec20_key
        row_dict["rec21_key"] = rec21_key
        row_dict["rec94_key"] = rec94_key
        #
        return rec38_key

    def define_fields_and_keys(self):
        """ """
        # Parameters for export.
        self.filter_parameters = [
            "# counted",
            "Wet weight",
            "Biovolume concentration",
            "Carbon concentration",
            "Cover (%)",
            "Carbon content",
        ]

        # ICES fields definitions.
        self.rec00_fields = [
            "RLABO-R00",
            "CNTRY-R00",
            "MYEAR-R00",
            "RFVER-R00",
        ]
        self.rec90_fields = [
            "SHIPC-R90",
            "CRUIS-R90",
            "OWNER-R90",
            "PRDAT-R90",
        ]
        self.rec91_fields = [
            "STNNO-R91",
            "LATIT-R91",
            "LONGI-R91",
            "POSYS-R91",
            "SDATE-R91",
            "STIME-R91",
            "ETIME-R91",
            "WADEP-R91",
            "STATN-R91",
            "MPROG-R91",
            "WLTYP-R91",
            "MSTAT-R91",
            "PURPM-R91",
            "EDATE-R91",
        ]
        # self.rec92_fields = ['RSRVD-R92', 'MATRX-R92', 'PARAM-R92', 'MUNIT-R92', 'VALUE']
        self.rec40_fields = [
            "TRANS-R40",
            "TRDGR-R40",
            "POSYS-R40",
            "LATRS-R40",
            "LNTRS-R40",
            "TRSLN-R40",
            "TREDT-R40",
            "LATRE-R40",
            "LNTRE-R40",
            "DEPAD-R40",
            "TREDP-R40",
            "MXVEG-R40",
            "SPVEG-R40",
            "R40-RLIST-NOT_USED-R40",
        ]
        self.rec34_fields = [
            "DTYPE-R34",
            "TRANS-R34",
            "SMPNO-R34",
            "SMLNK-R20",
            "ATIME-R34",
            "NOAGG-R34",
            "FNFLA-R34",
            "FINFL-R34",
            "SMVOL-R34",
            "WIRAN-R34",
            "CLMET-R34",
            "FLVOL-R34",
            "SUBST-R34",
            "DEPOS-R34",
            "PCNAP-R34",
            "PRSUB-R34",
            "TRSCS-R34",
            "TRSCE-R34",
            "NPORT-R34",
            "TRCSD-R34",
            "TRCED-R34",
        ]
        self.rec38_fields = [
            "MNDEP-R38",
            "MXDEP-R38",
            "SPECI-R38",
            "RLIST-R38",
            "SFLAG-R38",
            "STRID-R38",
            "SIZCL-R38",
            "RSRVD-R38",
            "MAGNI-R38",
            "COEFF-R38",
            "TRPHY-R38",
            "STAGE-R38",
            "SEXCO-R38",
            "PARAM-R38",
            "MUNIT-R38",
            "VFLAG-R38",
            "QFLAG-R38",
            "VALUE-R38",
            "CPORT-R38",
            "SDVOL-R38",
            "AMLNK-R21",
        ]
        self.rec20_fields = [
            "SLABO-R20",
            "SMLNK-R20",
            "SMTYP-R20",
            "NETOP-R20",
            "MESHS-R20",
            "SAREA-R20",
            "LNSMB-R20",
            "SPEED-R20",
            "PDMET-R20",
            "SPLIT-R20",
            "OBSHT-R20",
            "DURAT-R20",
            "DUREX-R20",
            "ESTFR-R20",
        ]
        self.rec21_fields = [
            "AMLNK-R21",
            "ALABO-R21",
            "METDC-R21",
            "REFSK-R21",
            "METST-R21",
            "METFP-R21",
            "METPT-R21",
            "METCX-R21",
            "METPS-R21",
            "METOA-R21",
            "AGDET-R21",
            "SREFW-R21",
            "SPECI-R21",
            "RLIST-R21",
            "ORGSP-R21",
            "SIZRF-R21",
            "FORML-R21",
            "ACCRD-R21",
            "ACORG-R21",
        ]
        self.rec94_fields = [
            "ICLNK-R94",
            "ICCOD-R94",
            "ICLAB-R94",
        ]

        # Key definitions.
        self.rec00_keys = []
        self.rec90_keys = [
            "CRUIS-R90",
        ]
        self.rec91_keys = [
            "CRUIS-R90",
            "STNNO-R91",
            "SDATE-R91",
            "STIME-R91",
        ]
        # self.rec92_keys = ['CRUIS-R90', 'STNNO-R91', ]
        self.rec40_keys = [
            "CRUIS-R90",
            "STNNO-R91",
            "SDATE-R91",
            "STIME-R91",
            "TRANS-R40",
        ]
        self.rec34_keys = [
            "CRUIS-R90",
            "STNNO-R91",
            "SDATE-R91",
            "STIME-R91",
            "TRANS-R40",
            "SMPNO-R34",
            "TRSCS-R34",
            "TRSCE-R34",
            "TRCSD-R34",
            "TRCED-R34",
        ]
        self.rec38_keys = [
            "CRUIS-R90",
            "STNNO-R91",
            "SDATE-R91",
            "STIME-R91",
            "TRANS-R40",
            "SMPNO-R34",
            "TRSCS-R34",
            "TRSCE-R34",
            "TRCSD-R34",
            "TRCED-R34",
            "STRID-R38",
            "SPECI-R38",
            "SIZCL-R38",
            "STAGE-R38",
            "SEXCO-R38",
            "PARAM-R38",
            "MUNIT-R38",
        ]
        self.rec20_keys = [
            "SMLNK-R20",
        ]
        self.rec21_keys = [
            "AMLNK-R21",
        ]
        self.rec94_keys = [
            "AMLNK-R21",
            "ICLNK-R94",
        ]

    def create_key_string(self, row_dict, key_columns):
        """ Util: Generates the key for one row. """
        key_string = ""
        try:
            key_list = [str(row_dict.get(item, "")) for item in key_columns]
            key_string = "+".join(key_list)
        except:
            key_string = "ERROR: Failed to generate key-string"
        # Replace swedish characters.
        key_string = key_string.replace("Å", "A")
        key_string = key_string.replace("Ä", "A")
        key_string = key_string.replace("Ö", "O")
        key_string = key_string.replace("å", "a")
        key_string = key_string.replace("ä", "a")
        key_string = key_string.replace("ö", "o")
        key_string = key_string.replace("µ", "u")
        #
        return key_string
