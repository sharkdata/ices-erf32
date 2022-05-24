#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import datetime
import logging
import erf32_generator


class ExportIcesContent(object):
    """ """

    def __init__(self, datarow_dict):
        """ """
        self._dict = datarow_dict
        self._export_stations = erf32_generator.global_export_stations
        self._translate_taxa = erf32_generator.global_translate_taxa
        self._translate_taxa_to_helcom_peg = (
            erf32_generator.global_translate_dyntaxa_to_helcom_peg
        )

        self.logger = logging.getLogger("erf32_generator")

    def copy_to_ices_fields(self):
        """ """
        # R00.FileInformation
        self._dict["RLABO-R00"] = "SMHI"
        self._dict["CNTRY-R00"] = "77"
        self._dict["MYEAR-R00"] = self._get_value("visit_year", "").replace(
            "-", ""
        )  # Format YYYYMMDD.
        self._dict["RFVER-R00"] = "3.2.5"

        # R90.SamplingPlatformRecord
        self._dict["SHIPC-R90"] = self._get_value("platform_code", "")
        self._dict["CRUIS-R90"] = self._get_value(
            "", ""
        )  # Will be generated in ices_expedition_key().
        self._dict["OWNER-R90"] = "SWAM"
        self._dict["PRDAT-R90"] = str(datetime.date.today()).replace(
            "-", ""
        )  # Format YYYYMMDD.

        # R91.SamplingEventRecord

        #         # Use shark_sample_id_md5 for PP, ZB and ZP. (PB later.)
        #         if self._get_value('delivery_datatype', '') in ['Phytoplankton', 'Zoobenthos', 'Zooplankton']: # Not: 'Phytobenthos', 'Epibenthos'
        #             self._dict['STNNO-R91'] = self._get_value('shark_sample_id_md5', '')
        #         if not self._dict.get('STNNO-R91', ''):
        #             stnno = self._get_value('station_name', '') + '-' + self._get_value('sample_date', '') + '-' + self._get_value('sample_time', '') # Must be unique.
        #             self._dict['STNNO-R91'] = stnno.replace('-', '') # '-' indicates error in DATSU.

        stnno = (
            self._get_value("sampling_laboratory_code", "")
            + "-"
            + self._get_value("platform_code", "")
            + "-"
            + self._get_value("station_name", "")
            + "-"
            + self._get_value("sample_date", "")
            + "-"
            + self._get_value("sample_time", "")
        )
        self._dict["STNNO-R91"] = stnno.replace(
            "-", ""
        )  # '-' indicates error in DATSU.

        #
        self._dict["LATIT-R91"] = self._get_value("sample_latitude_dd", "")
        self._dict["LONGI-R91"] = self._get_value("sample_longitude_dd", "")
        self._dict["POSYS-R91"] = self._get_value("positioning_system_code", "")
        self._dict["SDATE-R91"] = self._get_value("sample_date", "")
        self._dict["STIME-R91"] = self._get_value("sample_time", "")
        self._dict["ETIME-R91"] = ""  # Not used.
        self._dict["WADEP-R91"] = self._get_value("water_depth_m", "").replace(",", ".")
        self._dict["STATN-R91"] = self._get_value("station_name", "")

        mprog_default = self._get_value("monitoring_program_code", "")
        self._dict["MPROG-R91"] = self._export_stations.get_mprog(
            self._get_value("station_name", mprog_default)
        )
        self._dict["WLTYP-R91"] = self._export_stations.get_wltyp(
            self._get_value("station_name", "")
        )
        self._dict["MSTAT-R91"] = self._export_stations.get_mstat(
            self._get_value("station_name", "")
        )
        self._dict["PURPM-R91"] = self._export_stations.get_purpm(
            self._get_value("station_name", "")
        )
        self._dict["EDATE-R91"] = ""  # Not used.

        # R92.SiteDescriptionRecord
        self._dict["RSRVD-R92"] = ""  # Not used.
        self._dict["MATRX-R92"] = ""  # Not used.
        self._dict["PARAM-R92"] = ""  # Not use.
        self._dict["MUNIT-R92"] = ""  # Not used.
        self._dict["VALUE-R92"] = ""  # Not used.

        # R40.TransectDescription
        self._dict["TRANS-R40"] = self._get_value("transect_id", "")
        self._dict["TRDGR-R40"] = self._get_value("transect_direction", "")
        self._dict["POSYS-R40"] = self._get_value("positioning_system_code", "")
        self._dict["LATRS-R40"] = self._get_value("transect_start_latitude_dd", "")
        self._dict["LNTRS-R40"] = self._get_value("transect_start_longitude_dd", "")
        self._dict["TRSLN-R40"] = self._get_value("transect_length_m", "").replace(
            ",", "."
        )
        self._dict["TREDT-R40"] = ""
        self._dict["LATRE-R40"] = self._get_value("transect_end_latitude_dd", "")
        self._dict["LNTRE-R40"] = self._get_value("transect_end_longitude_dd", "")
        self._dict["DEPAD-R40"] = ""
        self._dict["TREDP-R40"] = ""
        self._dict["MXVEG-R40"] = ""
        self._dict["SPVEG-R40"] = ""
        self._dict["RLIST-R40"] = ""

        # R34.BiologicalCommunitySample
        self._dict["DTYPE-R34"] = self._get_value("delivery_datatype", "")
        self._dict["TRANS-R34"] = ""

        #         self._dict['SMPNO-R34'] = self._get_value('sample_id', '')
        self._dict["SMPNO-R34"] = self._get_value("shark_sample_id_md5", "")

        self._dict["SMLNK-R20"] = ""  # Generated later.
        self._dict["ATIME-R34"] = ""  # Not used.
        self._dict["NOAGG-R34"] = self._get_value("aggregated_subsamples", "")
        self._dict["FNFLA-R34"] = self._get_value("fauna_flora_found", "")
        self._dict["FINFL-R34"] = self._get_value("factors_influencing_code", "")
        self._dict["SMVOL-R34"] = self._get_value("sampled_volume_l", "")
        self._dict["WIRAN-R34"] = ""
        self._dict["CLMET-R34"] = self._get_value("calculation_method", "")
        self._dict["FLVOL-R34"] = ""
        self._dict["SUBST-R34"] = ""
        self._dict["DEPOS-R34"] = self._get_value("sediment_deposition_code", "")
        self._dict["PCNAP-R34"] = ""
        self._dict["PRSUB-R34"] = ""
        self._dict["TRSCS-R34"] = self._get_value(
            "section_distance_start_m", ""
        ).replace(",", ".")
        self._dict["TRSCE-R34"] = self._get_value("section_distance_end_m", "").replace(
            ",", "."
        )
        self._dict["TRCSD-R34"] = self._get_value("section_start_depth_m", "").replace(
            ",", "."
        )
        self._dict["NPORT-R34"] = self._get_value("number_of_portions", "").replace(
            ",", "."
        )

        try:
            number_of_portions_integer = int(
                float(self._get_value("number_of_portions", ""))
            )
            self._dict["NPORT-R34"] = str(number_of_portions_integer)
        except:
            pass

        self._dict["TRCED-R34"] = self._get_value("section_end_depth_m", "").replace(
            ",", "."
        )

        # R38.BiologicalCommunityAbundance
        self._dict["MNDEP-R38"] = self._get_value("sample_min_depth_m", "").replace(
            ",", "."
        )
        self._dict["MXDEP-R38"] = self._get_value("sample_max_depth_m", "").replace(
            ",", "."
        )
        self._dict["SPECI-R38"] = self._get_value("scientific_name", "")
        self._dict["RLIST-R38"] = ""  # Generated later.
        self._dict["SFLAG-R38"] = self._get_value("species_flag_code", "")
        self._dict["STRID-R38"] = self._get_value("stratum_id", "")
        self._dict["SIZCL-R38"] = self._get_value("size_class", "")
        self._dict["RSRVD-R38"] = ""  # Not used.
        self._dict["MAGNI-R38"] = self._get_value("magnification", "")
        self._dict["COEFF-R38"] = self._get_value("coefficient", "")
        self._dict["TROPY-R38"] = self._get_value("trophic_type_code", "")
        self._dict["STAGE-R38"] = self._get_value("dev_stage_code", "")
        self._dict["SEXCO-R38"] = self._get_value("sex_code", "")
        self._dict["PARAM-R38"] = self._get_value("parameter", "")
        self._dict["MUNIT-R38"] = self._get_value("unit", "")
        self._dict["VFLAG-R38"] = ""  # Not used.
        self._dict["QFLAG-R38"] = self._get_value("quality_flag", "")
        self._dict["VALUE-R38"] = self._get_value("value", "")

        try:
            counted_portions_integer = int(
                float(self._get_value("counted_portions", ""))
            )
            self._dict["CPORT-R38"] = str(counted_portions_integer)
        except:
            cport_str = str(self._get_value("counted_portions", ""))
            if cport_str != "":
                self.logger.error("Failed to convert to float. CPORT: " + cport_str)

        self._dict["SDVOL-R38"] = self._get_value("sedimentation_volume_ml", "")
        self._dict["AMLNK-R21"] = ""  # Generated later.

        # R20.SamplingMethod
        self._dict["SLABO-R20"] = self._get_value("sampling_laboratory_code", "")
        self._dict["SMLNK-R20"] = ""  # Generated later.
        self._dict["SMTYP-R20"] = self._get_value("sampler_type_code", "")
        self._dict["NETOP-R20"] = ""
        
        # Mesh size. Use either mesh_size_um or lower_mesh_size_um.
        mesh_size_um = self._get_value("mesh_size_um", "")
        if mesh_size_um == "":
            mesh_size_um = self._get_value("lower_mesh_size_um", "")
        self._dict["MESHS-R20"] = mesh_size_um

        self._dict["SAREA-R20"] = self._get_value("sampler_area_cm2", "")
        self._dict["LNSMB-R20"] = ""  # Not used.
        self._dict["SPEED-R20"] = ""
        self._dict["PDMET-R20"] = self._get_value("plankton_sampling_method_code", "")
        self._dict["SPLIT-R20"] = self._get_value("sample_splitting_code", "")
        self._dict["OBSHT-R20"] = ""
        self._dict["DURAT-R20"] = ""
        self._dict["DUREX-R20"] = ""
        self._dict["ESTRF-R20"] = ""

        # R21.AnalyticalMethod
        self._dict["AMLNK-R21"] = ""  # Generated later.
        self._dict["ALABO-R21"] = self._get_value("analytical_laboratory_code", "")
        self._dict["METDC-R21"] = self._get_value("method_documentation", "")
        self._dict["REFSK-R21"] = self._get_value("reference_source_code", "")
        self._dict["METST-R21"] = self._get_value("storage_method_code", "")
        self._dict["METFP-R21"] = self._get_value("preservation_method_code", "")
        self._dict["METPT-R21"] = ""
        self._dict["METCX-R21"] = ""
        self._dict["METPS-R21"] = ""
        self._dict["METOA-R21"] = self._get_value("analysis_method_code", "")
        self._dict["AGDET-R21"] = ""
        self._dict["SREFW-R21"] = ""
        self._dict["SPECI-R21"] = ""
        self._dict["RLIST-R21"] = ""
        self._dict["ORGSP-R21"] = ""
        self._dict["SIZRF-R21"] = self._get_value("size_class_ref_list", "")
        self._dict["FORML-R21"] = ""
        self._dict["ACCRD-R21"] = ""
        self._dict["ACORG-R21"] = ""

        # R94.Intercomparison
        self._dict["ICLNK-R94"] = ""
        self._dict["ICCOD-R94"] = ""
        self._dict["ICLAB-R94"] = ""

    def cleanup_ices_fields(self):
        """ """
        if not self._dict["MPROG-R91"]:
            self._dict["MPROG-R91"] = "NATL"
        #
        if not self._dict["SMPNO-R34"]:
            self._dict["SMPNO-R34"] = "9999"
        #
        sample_part_id = self._dict.get("sample_part_id", "")
        if sample_part_id:
            self._dict["SMPNO-R34"] = self._dict["SMPNO-R34"] + "-" + sample_part_id

        #
        self._dict["METDC-R21"] = ""
        self._dict["REFSK-R21"] = "HC-C-C8"
        #
        if not self._dict["ALABO-R21"]:
            self._dict["ALABO-R21"] = self._get_value(
                "analytical_laboratory_name_en", ""
            )
        if not self._dict["ALABO-R21"]:
            self._dict["ALABO-R21"] = self._get_value(
                "analytical_laboratory_name_sv", ""
            )
        #
        if not self._dict["SLABO-R20"]:
            self._dict["SLABO-R20"] = self._get_value("sampling_laboratory_name_en", "")
        if not self._dict["SLABO-R20"]:
            self._dict["SLABO-R20"] = self._get_value("sampling_laboratory_name_sv", "")
        #
        if not self._dict["SHIPC-R90"]:
            self._dict["SHIPC-R90"] = "AA30"  # Unspecified ship.
        #
        self._dict["SDATE-R91"] = self.ices_date(self._dict["SDATE-R91"])
        self._dict["EDATE-R91"] = self.ices_date(self._dict["SDATE-R91"])
        #
        self._dict["STIME-R91"] = self.ices_time(self._dict["STIME-R91"])
        self._dict["ETIME-R91"] = self.ices_time(self._dict["ETIME-R91"])
        self._dict["ATIME-R34"] = self.ices_time(self._dict["ATIME-R34"])
        #         #
        #         self._dict['LATIT-R91'] = self.ices_lat_long(self._dict['LATIT-R91'])
        #         self._dict['LONGI-R91'] = self.ices_lat_long(self._dict['LONGI-R91'])
        #
        self._dict["DTYPE-R34"] = self.ices_datatype(self._dict["DTYPE-R34"])
        #
        #         self._dict['PARAM-R38'] = self.ices_parameter_name(self._dict['PARAM-R38'])
        self._dict["PARAM-R38"] = self.ices_parameter_name(self._dict)
        #
        #         self._dict['MUNIT-R38'] = self.ices_unit_name(self._dict['MUNIT-R38'])
        self._dict["MUNIT-R38"] = self.ices_unit_name(self._dict)
        #
        # Fauna-flora-found.
        if self._dict["DTYPE-R34"] in ["PB", "ZB"]:
            if not self._dict["FNFLA-R34"]:
                self._dict["FNFLA-R34"] = "Y"

        # Translate species names.

        # Phytoplankton.
        if self._dict["DTYPE-R34"] == "PP":
            (scientific_name, rlist) = self.translate_scientific_name_to_helcom_peg(
                self._get_value("scientific_name", self._dict["SPECI-R38"])
            )
            if scientific_name:
                self._dict["SPECI-R38"] = scientific_name
            if rlist:
                self._dict["RLIST-R38"] = rlist
                self._dict["SIZRF-R21"] = "PEG_BVOL2017"
            else:
                self._dict["RLIST-R38"] = "PEG_BVOL"
                self._dict["SIZRF-R21"] = "PEG_BVOL2017"
            #
            self._dict["PDMET-R20"] = "IND"

        else:
            # Aphia ID now included i SHARK zip files.
            aphia_id = self._dict.get("aphia_id", "")
            if aphia_id:
                self._dict["SPECI-R38"] = aphia_id
                self._dict["RLIST-R38"] = "ERID"
            else:
                # Other.
                (aphiaid, rlist) = self.translate_scientific_name_to_aphia_id(
                    self._dict["SPECI-R38"]
                )
                if aphiaid:
                    self._dict["SPECI-R38"] = aphiaid
                if rlist:
                    self._dict["RLIST-R38"] = rlist

        #
        # Add depth if missing.
        if self._dict["DTYPE-R34"] == "ZB":
            if len(self._dict["WADEP-R91"]) == 0:
                self._dict["WADEP-R91"] = self._dict["MNDEP-R38"]
            # In Zoobenthos: MNDEP = Upper depth of sediment sample.
            self._dict["MNDEP-R38"] = ""
            # In Zoobenthos: MXDEP = Lower depth of sediment sample.
            self._dict["MXDEP-R38"] = ""
        #
        # No analysis lab for some PB. Use sampling lab.
        if self._dict["DTYPE-R34"] == "PB":
            if self._dict["ALABO-R21"] in ["", "-"]:
                self._dict["ALABO-R21"] = self._dict["SLABO-R20"]
        #
        # Generate expedition key.
        self._dict["CRUIS-R90"] = self.ices_expedition_key()
        #
        # Tilde.
        self._dict["POSYS-R91"] = self.ices_tilde(self._dict["POSYS-R91"])
        self._dict["POSYS-R40"] = self.ices_tilde(self._dict["POSYS-R40"])
        self._dict["MPROG-R91"] = self.ices_tilde(self._dict["MPROG-R91"])
        self._dict["WLTYP-R91"] = self.ices_tilde(self._dict["WLTYP-R91"])
        self._dict["MSTAT-R91"] = self.ices_tilde(self._dict["MSTAT-R91"])
        self._dict["PURPM-R91"] = self.ices_tilde(self._dict["PURPM-R91"])
        self._dict["SFLAG-R38"] = self.ices_tilde(self._dict["SFLAG-R38"])
        self._dict["VFLAG-R38"] = self.ices_tilde(self._dict["VFLAG-R38"])

        #
        if self._dict["DTYPE-R34"] in ["PB"]:
            if not self._dict["SMTYP-R20"]:
                self._dict["SMTYP-R20"] = "DTR"  # Diving transect.

        # Fix for ZB with size classes. 
        # Add size class from ICES vocab: https://vocab.ices.dk/?ref=48

        if self._dict["DTYPE-R34"] == "ZP":
            size_class  = self._dict.get("size_class", "")
            size_min_um = self._dict.get("size_min_um", "")
            size_max_um = self._dict.get("size_max_um", "")
            if (size_class == "") and size_min_um and size_max_um:
                
                if (size_min_um == "0") and (size_max_um == "60"):
                    self._dict["SIZCL-R38"] = "26"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "0") and (size_max_um == "120"):
                    self._dict["SIZCL-R38"] = "27"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "61") and (size_max_um == "120"):
                    self._dict["SIZCL-R38"] = "29"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "141") and (size_max_um == "200"):
                    self._dict["SIZCL-R38"] = "30"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "121") and (size_max_um == "200"):
                    self._dict["SIZCL-R38"] = "34"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "121") and (size_max_um == "220"):
                    self._dict["SIZCL-R38"] = "35"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "121") and (size_max_um == "140"):
                    self._dict["SIZCL-R38"] = "36"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "201") and (size_max_um == "260"):
                    self._dict["SIZCL-R38"] = "38"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "201") and (size_max_um == "220"):
                    self._dict["SIZCL-R38"] = "39"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "201") and (size_max_um == "250"):
                    self._dict["SIZCL-R38"] = "40"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "221") and (size_max_um == "400"):
                    self._dict["SIZCL-R38"] = "41"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "261") and (size_max_um == "340"):
                    self._dict["SIZCL-R38"] = "42"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "341") and (size_max_um == "400"):
                    self._dict["SIZCL-R38"] = "43"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "401") and (size_max_um == "800"):
                    self._dict["SIZCL-R38"] = "44"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "801") and (size_max_um == "1200"):
                    self._dict["SIZCL-R38"] = "65"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "801") and (size_max_um == "1000"):
                    self._dict["SIZCL-R38"] = "66"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "1001") and (size_max_um == "1200"):
                    self._dict["SIZCL-R38"] = "67"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "1201") and (size_max_um == "1400"):
                    self._dict["SIZCL-R38"] = "68"
                    self._dict["SIZRF-R21"] = "SIZGL"
                elif (size_min_um == "1401") and (size_max_um == "1600"):
                    self._dict["SIZCL-R38"] = "69"
                    self._dict["SIZRF-R21"] = "SIZGL"
                else:
                    self.logger.warning(
                        "ZB: No size class for: " + size_min_um + " - " + size_max_um
                    )

            # if size_min_um and size_max_um:
            #     c = size_min_um + "-" + size_max_um
            #     self._dict["SPECI-R38"] = (
            #         "<REMOVE>" + self._dict["SPECI-R38"]
            #     )  # Is removed when generating Erf32 file.
            # elif size_min_um:
            #     self._dict["SIZCL-R38"] = size_min_um
            #     self._dict["SPECI-R38"] = (
            #         "<REMOVE>" + self._dict["SPECI-R38"]
            #     )  # Is removed when generating Erf32 file.
            # elif size_max_um:
            #     self._dict["SIZCL-R38"] = size_max_um
            #     self._dict["SPECI-R38"] = (
            #         "<REMOVE>" + self._dict["SPECI-R38"]
            #     )  # Is removed when generating Erf32 file.


        #### OLD SOLUTION ####
        # # Temporary fix for ZB with sizes.
        # if self._dict["DTYPE-R34"] == "ZP":
        #     size_min_um = self._dict.get("size_min_um", "")
        #     size_max_um = self._dict.get("size_max_um", "")
        #     if size_min_um and size_max_um:
        #         c = size_min_um + "-" + size_max_um
        #         self._dict["SPECI-R38"] = (
        #             "<REMOVE>" + self._dict["SPECI-R38"]
        #         )  # Is removed when generating Erf32 file.
        #     elif size_min_um:
        #         self._dict["SIZCL-R38"] = size_min_um
        #         self._dict["SPECI-R38"] = (
        #             "<REMOVE>" + self._dict["SPECI-R38"]
        #         )  # Is removed when generating Erf32 file.
        #     elif size_max_um:
        #         self._dict["SIZCL-R38"] = size_max_um
        #         self._dict["SPECI-R38"] = (
        #             "<REMOVE>" + self._dict["SPECI-R38"]
        #         )  # Is removed when generating Erf32 file.

        # QFLAG=B or S not accepted. S and B saved as VFLAG=S.
        qflag = self._dict["QFLAG-R38"]
        vflag = self._dict["VFLAG-R38"]
        if qflag in ["B", "S"]:
            self._dict["QFLAG-R38"] = ""
            self._dict["VFLAG-R38"] = "S"


        # Convert SMVOL from litre to m3 .
        if self._dict["DTYPE-R34"] == "ZP":
            sampled_volume_l = self._get_value("sampled_volume_l", "")
            sampled_volume_l = float(sampled_volume_l)
            sampled_volume_m3 = sampled_volume_l / 1000.0
            self._dict["SMVOL-R34"] = str(sampled_volume_m3)



    def check_zp_abundnr_wetwt(self, datarow_dict, zp_abundnr_wetwt_list):
        """ "ZP must have both ABUNDNR and WETWT."""
        if self._dict["DTYPE-R34"] == "ZP":
            param = self._dict["PARAM-R38"]
            if param in [
                "ABUNDNR",
                "BMWETWT",
            ]:
                rec38_key = self._dict["rec38_key"]
                zp_abundnr_wetwt_list.append(rec38_key)

    def add_transect_fields(self):
        """ """
        transect_data_dict = erf32_generator.global_transect_data.get_transect_data(
            self._dict
        )

        if self._dict["DTYPE-R34"] == "PB":  # or \
            # (self._dict['DTYPE-R34'] == 'ZB'):

            self._dict["TRANS-R40"] = transect_data_dict.get("transect_sequence_no", "")

            # Get max calculated distance end from sections.
            if self._dict["TRSLN-R40"] == "":
                self._dict["TRSLN-R40"] = transect_data_dict.get(
                    "max_section_distance_end_m", ""
                )
            # Add some default values if the corresponding field values are empty.
            if (
                ("Skagerack" in self._get_value("dataset_file_name", ""))
                or ("Skagerrak" in self._get_value("dataset_file_name", ""))
                or ("Skagerrack" in self._get_value("dataset_file_name", ""))
                or ("Skagerak" in self._get_value("dataset_file_name", ""))
                or ("SHARK_Epibenthos_2021_SLC-T" in self._get_value("dataset_file_name", ""))
            ):
                self._dict["TREDT-R40"] = "CR"  # TREDT.
                self._dict["TRSLN-R40"] = transect_data_dict.get(
                    "max_sample_max_depth_m", ""
                )  # TRSLN.
                self._dict["DEPAD-R40"] = "N"  # DEPAD.
                self._dict["SMTYP-R20"] = "DIV-PHOT"  # SMTYP.

                self._dict["LATRS-R40"] = self._get_value(
                    "sample_latitude_dd", ""
                ).replace(",", ".")
                self._dict["LNTRS-R40"] = self._get_value(
                    "sample_longitude_dd", ""
                ).replace(",", ".")
                self._dict["LATRE-R40"] = self._get_value(
                    "sample_latitude_dd", ""
                ).replace(",", ".")
                self._dict["LNTRE-R40"] = self._get_value(
                    "sample_longitude_dd", ""
                ).replace(",", ".")

                self._dict["TRSCS-R34"] = self._get_value(
                    "sample_min_depth_m", ""
                ).replace(",", ".")
                self._dict["TRSCE-R34"] = self._get_value(
                    "sample_max_depth_m", ""
                ).replace(",", ".")

                self._dict["TRCSD-R34"] = self._get_value(
                    "sample_min_depth_m", ""
                ).replace(",", ".")
                self._dict["TRCED-R34"] = self._get_value(
                    "sample_max_depth_m", ""
                ).replace(",", ".")

            else:
                self._dict["TREDT-R40"] = "DS"  # TREDT.
                #####self._dict['TRSLN-R40'] = '0' # TRSLN.
                self._dict["DEPAD-R40"] = "N"  # DEPAD.
            #
            stratum_id = erf32_generator.global_transect_data.stratum_id(self._dict)
            self._dict["STRID-R38"] = stratum_id

            ##### Calculated sampler area SAREA. #####
            ##### TODO: Move to an earlier stage in the data flow. For example SHARKadm. #####
            ##### Calculated sampler area SAREA. #####

            # Start with a check if m2 is used.
            if self._get_value("SAREA-R20") == "":
                try:
                    sarea_value = self._get_value("sampler_area_m2", "")
                    if sarea_value:
                        sarea_value = float(sarea_value) * 10000
                        sarea_value = str(sarea_value)
                        self._dict["SAREA-R20"] = str(sarea_value)
                    else:
                        self._dict["SAREA-R20"] = self._get_value(
                            "sampler_area_cm2", ""
                        )
                except:
                    self._dict["SAREA-R20"] = self._get_value("sampler_area_cm2", "")

            if self._get_value("SAREA-R20") == "":
                sampler_area_opening = ""

                # Skagerack.
                if (
                    ("Skagerack" in self._get_value("dataset_file_name", ""))
                    or ("Skagerrak" in self._get_value("dataset_file_name", ""))
                    or ("Skagerrack" in self._get_value("dataset_file_name", ""))
                    or ("Skagerak" in self._get_value("dataset_file_name", ""))
                ):
                    sampler_area_opening = "2500"

                # Kattegatt.
                if "Kattegatt" in self._get_value("dataset_file_name", ""):
                    try:
                        section_end = float(
                            self._get_value("section_distance_end_m").replace(",", ".")
                        )
                        section_start = float(
                            self._get_value("section_distance_start_m").replace(
                                ",", "."
                            )
                        )
                        #
                        sarea = (section_end - section_start) * 100.0 * 400.0
                        sarea = round(sarea * 1.0) / 1.0  # No decimals.
                        sampler_area_opening = str(sarea)  # ICES: SAREA.
                    except:
                        sampler_area_opening = ""
                #                         print('ICES: Failed to calculate SAREA for' +
                #                               ' Station: ' + self._get_value('station_name') +
                #                               ' Date: ' + self._get_value('sample_date'))

                # DEEP=SUSE and Linné university.
                if ("_DEEP_" in self._get_value("dataset_file_name")) or (
                    "_LNU_" in self._get_value("dataset_file_name")
                ):
                    try:
                        section_end = float(
                            self._get_value("section_distance_end_m").replace(",", ".")
                        )
                        section_start = float(
                            self._get_value("section_distance_start_m").replace(
                                ",", "."
                            )
                        )
                        transect_width = float(
                            self._get_value("transect_width_m").replace(",", ".")
                        )
                        #
                        sarea = (section_end - section_start) * transect_width * 10000.0
                        sarea = round(sarea * 1.0) / 1.0  # No decimals.
                        sampler_area_opening = str(sarea)  # ICES: SAREA.
                    except:
                        sampler_area_opening = ""
                        try:
                            self.logger.warning(
                                "ICES: Failed to calculate SAREA for"
                                + "  Station: "
                                + self._get_value("station_name")
                                + "  Date: "
                                + str(self._get_value("sample_date"))
                                + "  Section distance end m: "
                                + str(self._get_value("section_distance_end_m"))
                                + "  Section distance start m: "
                                + str(self._get_value("section_distance_start_m"))
                                + "  Transect width m: "
                                + str(self._get_value("transect_width_m"))
                            )
                        except:
                            pass
                    #
                self._dict["SAREA-R20"] = sampler_area_opening

            #             # TEST TEST
            #             if self._get_value('SAREA-R20') == '':
            #                 print('SAREA=0: Parameter: ' + self._get_value('parameter') + '   Dataset: ' + self._get_value('dataset_name'))

            # DTR = Diving transect.
            if self._get_value("SMTYP-R20") == "":
                self._dict["SMTYP-R20"] = "DTR"

            # For section (default)                  For sample squares (conditional)
            # TRSCS = section_distance_start_m       transect_min_distance_m
            # TRSCE = section_distance_end_m         transect_min_distance_m
            # För avsnitten (default)                För provrutorna (conditional)
            # TRCSD = section_start_depth_m          sample_min_depth_m
            # TRCED = section_end_depth_m            sample_max_depth_m

            if (not self._get_value("TRSCS-R34")) and (
                not self._get_value("TRSCE-R34")
            ):

                self._dict["TRSCS-R34"] = self._get_value("transect_min_distance_m")
                self._dict["TRSCE-R34"] = self._get_value("transect_max_distance_m")
                # self._dict["TRCSD-R34"] = self._get_value("sample_min_depth_m")
                # self._dict["TRCED-R34"] = self._get_value("sample_max_depth_m")

            if not self._get_value("TRCSD-R34"):
                self._dict["TRCSD-R34"] = self._get_value("sample_min_depth_m")
            if not self._get_value("TRCSD-R34"):
                self._dict["TRCSD-R34"] = self._get_value("sample_depth_m")

            if not self._get_value("TRCED-R34"):
                self._dict["TRCED-R34"] = self._get_value("sample_max_depth_m")
            if not self._get_value("TRCED-R34"):
                self._dict["TRCED-R34"] = self._get_value("sample_depth_m")

            # If depth > 0: Set depth to 0 and DEPAD=I1.
            section_start_depth_m = self._get_value("section_start_depth_m", "")
            try:
                if section_start_depth_m:
                    section_start_depth_m = float(
                        section_start_depth_m.replace(",", ".")
                    )
                    if section_start_depth_m < 0.0:
                        self._dict["TRCSD-R34"] = "0"
                        self._dict["DEPAD-R40"] = "I1"
            except:
                self.logger.warning("DEBUG: Failed to convert to float.")
                pass

        # Remove values above the surface. ICES does not accept them.
        for ices_field_name in [
            "TREDP-R40",
            "TRCSD-R34",
            "TRCED-R34",
            "MNDEP-R38",
            "MXDEP-R38",
        ]:
            depth_s = self._get_value(ices_field_name, "")
            try:
                if depth_s:
                    depth_s = float(depth_s.replace(",", "."))
                    if depth_s < 0.0:
                        self._dict[ices_field_name] = "0"
                        self.logger.warning(
                            "DEBUG: Depth value set to zero: "
                            + ices_field_name
                            + "   Value: "
                            + str(depth_s)
                        )
            except:
                self.logger.warning(
                    "DEBUG: Failed to convert to float. "
                    + ices_field_name
                    + "   Value: "
                    + str(depth_s)
                )
                pass


        # # NOTE: Can't handle transects with mixed FRAMENET and non FRAMENET.
        # # FRAMENET and DIV are not collected as transect data.
        # if self._dict.get("sampler_type_code", "") in ["FRAMENET", "DIV"]:
        #     self._dict["TRCSD-R34"] = ""
        #     self._dict["TRCED-R34"] = ""




    def add_rec20(self, rec20_dict, rec20_fields):
        """ """
        #         self.rec20_fields = ['SLABO', 'SMLNK', 'SMTYP', 'MESHS', 'SAREA', 'LNSMB']
        #
        r20_key_list = []
        r20_dict = {}
        for key in rec20_fields:
            r20_key_list.append(str(self._get_value(key, "")))
            r20_dict[key] = self._get_value(key, "")
        #
        r20_key = "-".join(r20_key_list)
        if r20_key not in rec20_dict:
            rec20_dict[r20_key] = r20_dict
            sequence_number = str(len(rec20_dict))
            rec20_dict[r20_key]["sequence_number"] = sequence_number
        #
        self._dict["SMLNK-R20"] = rec20_dict[r20_key]["sequence_number"]

    def add_rec21(self, rec21_dict, rec21_fields):
        """ """
        r21_key_list = []
        r21_dict = {}
        for key in rec21_fields:
            r21_key_list.append(str(self._get_value(key, "")))
            r21_dict[key] = self._get_value(key, "")
        #
        r21_key = "-".join(r21_key_list)
        if r21_key not in rec21_dict:
            rec21_dict[r21_key] = r21_dict
            sequence_number = str(len(rec21_dict))
            rec21_dict[r21_key]["sequence_number"] = sequence_number
        #
        self._dict["AMLNK-R21"] = rec21_dict[r21_key]["sequence_number"]

    # ===== Utils =====
    def _get_value(self, internal_key, default=""):
        """ """
        value = self._dict.get(internal_key, default)  #
        return value

    def translate_scientific_name_to_aphia_id(self, scientific_name):
        """ """
        aphiaid = self._translate_taxa.get_translated_to_aphiaid(scientific_name)
        #
        if not aphiaid:
            # Fallback if not found.
            return (scientific_name, "ER")
        #
        return (aphiaid, "ERID")

    def translate_scientific_name_to_helcom_peg(self, scientific_name):
        """ """
        (
            helcom_peg_scientific_name,
            rlist,
        ) = self._translate_taxa_to_helcom_peg.get_translated_taxa_and_rlist(
            scientific_name
        )
        #
        return (helcom_peg_scientific_name, rlist)

    def ices_expedition_key(self):
        """ """
        key_list = []
        # Part 1.
        key_list.append(self._dict.get("MYEAR-R00", ""))  #
        key_list.append(
            self._dict.get("RLABO-R00", "")
        )  # visit.getParent().getReporting_institute_code()
        key_list.append(
            self._dict.get("DTYPE-R34", "")
        )  # IcesUtil.convertToIcesDatatype(visit
        # Part 2.
        key_list.append(self._dict.get("SHIPC-R90", ""))
        # Part 3.
        month = self._dict.get("SDATE-R91", "YYYYMMDD")[4:6]
        key_list.append(month)
        #
        key = "-".join(key_list)
        return key

    def ices_tilde(self, value):
        """ """
        # ICES use ~ as delimiter if multiple flags are used.
        tmp_string = value.strip()
        if "," in tmp_string:
            return tmp_string.replace(",", "~").replace(" ", "")
        if " " in tmp_string:
            return tmp_string.replace(" ", "~")
        #
        return tmp_string

    def ices_date(self, date):
        """ """
        ices_date = date.replace("-", "")
        return ices_date

    def ices_time(self, time):
        """ """
        ices_time = time.replace(":", "")
        return ices_time[0:4]

    def ices_datatype(self, long_name):
        """ """
        datatype = "<<NO DATATYPE FOUND>>"
        if long_name == "Phytobenthos":
            datatype = "PB"
        elif long_name == "Epibenthos":
            datatype = "PB"
        elif long_name == "Phytoplankton":
            datatype = "PP"
        elif long_name == "Zoobenthos":
            datatype = "ZB"
        elif long_name == "Zooplankton":
            datatype = "ZP"
        else:
            self.logger.warning("DEBUG: Invalid datatype: " + long_name)
        #
        return datatype

    def ices_parameter_name(self, row_dict):
        """ """
        #         value = row_dict['PARAM-R38']
        value = row_dict["parameter"]

        if value == "# counted":
            return "ABUNDNR"
        elif value == "Wet weight":
            return "BMWETWT"
        elif value == "Biovolume concentration":
            return "BMCEVOL"  # PP: Biovolume concentration, mm3/l, BMCEVOL.
        elif value == "Carbon concentration":
            return "BMCCONT"  # PP: Carbon concentration, ugC/l, BMCCONT.
        elif value == "Cover (%)":
            return "ABUND%C"  # Epibenthos.
        # ZP.
        if value == "Carbon content":
            unit_value = row_dict["MUNIT-R38"]
            if unit_value == "ug/m3":
                return "BMCCONT"  # ZP: Carbon content, ug/m3, BMCCONT.
        #
        return value

    def ices_unit_name(self, row_dict):
        """ """
        unit_name = row_dict["MUNIT-R38"]

        if unit_name == "nr/l":
            return "nr/dm3"
        elif unit_name == "ind":
            return "nr"
        elif unit_name == "ind/analysed sample fraction":
            return "nr"
        elif unit_name == "g/analysed sample fraction":
            return "g"

        elif unit_name == "mg/analysed sample fraction":
            if self._dict["parameter"] == "Wet weight":
                try:
                    # Also divide value by 1000.
                    value = float(self._dict.get("VALUE-R38", ""))
                    new_value = value / 1000
                    if value > 0.001:
                        self._dict["VALUE-R38"] = "{:f}".format(new_value).replace(
                            ",", "."
                        )
                    else:
                        self._dict["VALUE-R38"] = "{:10.9f}".format(new_value).replace(
                            ",", "."
                        )
                    # New unit.
                    unit_name = "g"
                except:
                    self.logger.warning(
                        "DEBUG: Failed to divide value by 1000: "
                        + self._dict.get("VALUE-R38", "")
                    )
        elif unit_name == "ugC/l":
            if self._dict["parameter"] == "Carbon concentration":
                return "ug/l"
        #
        return unit_name

    def is_kingdom_animalia(self):
        """ """
        if "Animalia" in self._dict.get("taxon_hierarchy", ""):
            return True
        #
        return False


#     def fix_sample_number(self, value):
#         """ """
#         if not value:
#             return '0' # ICES needs a value.
#         elif len(value) > 12:
#             # SMHI PP contains longer id:s than accepted by ICES. Remove middle part.
#             first_and_last_part = value[0, 5] + '--' + value[-5:]
#             return first_and_last_part
#         #
#         return value.replace(',', '.')

#     def ices_fauna_flora_found(self, value):
#         """ """
#         if value == '0': return 'Y'
#         if value == '1': return 'N'
#         return value

#     def ices_sediment_deposit(self, value):
#         """ """
#         # DEPOS, Sediment deposit.
#         if value == '1': return 'N'
#         if value == '2': return 'L'
#         if value == '3': return 'M'
#         if value == '4': return 'H'
#         return value

#     def ices_quality_flag(self, value):
#         """ """
#         delimiter = ' '
#         if ',' in value: delimiter = ','
#         parts = value.trim().split(delimiter)
#
#         string_list = []
#         for part in parts:
#             part = parts.trim()
#             if not part:
#                 pass
#             elif part =='A':
#                 pass # 'A' should not be reported to ICES.
#             elif part == 'S':
#                 string_list.append("<<S:suspect value>>") # Indicator for manual removal of QFLAG or rec38-row.
#             else:
#                 string_list.append(part)
#         #
#         return '~'.join(string_list)
