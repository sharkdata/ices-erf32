#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import logging
import datetime
import erf32_generator


class IcesErf32Generator:
    """ """

    def __init__(self):
        """ """
        self.logger = None

    def generate_erf32(self, config_file):
        """ """
        # Config and metadata content.
        ices_config = erf32_generator.GeneratorConfig(config_file)
        ices_config.load_config()

        # Load resource content for ICES station.
        erf32_generator.global_export_stations.load_export_stations()
        # Load resource content to translate from DynTaxa to WoRMS.
        erf32_generator.global_translate_taxa.load_translate_taxa()
        # Load resource content to translate from DynTaxa to Helcom PEG.
        erf32_generator.global_translate_dyntaxa_to_helcom_peg.load_translate_taxa()
        # Filters and translate.
        erf32_generator.global_filters.load_filters(ices_config.filters_files)
        erf32_generator.global_translate.load_translate(ices_config.translate_files)

        # Iterate over years. One report for each year.
        year_int = int(ices_config.year_from)
        year_to_int = int(ices_config.year_to)
        while year_int <= year_to_int:
            """ """
            datatype = ices_config.datatype
            today = datetime.date.today().isoformat()
            # Target file for current year.
            target_file_name = ices_config.target_file_template
            target_file_name = target_file_name.replace("<DATATYPE>", datatype)
            target_file_name = target_file_name.replace("<YEAR>", str(year_int))
            target_file_name = target_file_name.replace("<DATE>", today)
            # Log file for current year.
            log_file_name = ices_config.target_logfile_template
            log_file_name = log_file_name.replace("<DATATYPE>", datatype)
            log_file_name = log_file_name.replace("<YEAR>", str(year_int))
            log_file_name = log_file_name.replace("<DATE>", today)
            # Setup logging.
            logger = logging.getLogger("erf32_generator")
            self.logger = logger
            self.setup_logging(log_file_name)
            print("")
            print("")
            logger.info("")
            logger.info(
                "=== Processing: " + str(config_file) + ". Year: " + str(year_int)
            )
            logger.info("")
            logger.info("Files to process: ")
            for source_file in ices_config.source_files:
                logger.info("- " + source_file)

            # Prepare data.
            logger.info("")
            logger.info("=== Preparing data ===")

            erf32_generator.global_export_stations.clear_missing_station_list()
            erf32_generator.global_translate_taxa.clear_missing_taxa_list()
            try:
                source_data = erf32_generator.Erf32DataShark(ices_config)
                for dataset_filepath in ices_config.source_files:
                    source_data.add_shark_dataset(dataset_filepath, year_int)
                # Data result.
                data_rows = source_data.get_data_rows()
                logger.info("")
                logger.info("Total number of data rows: " + str(len(data_rows)))

                logger.info("")
                logger.info("=== Generate ICES ERF32 ===")
                generator = erf32_generator.GenerateIcesErf32()
                generator.setup(data_rows)
                error_counter = 0
                status = ""
                user = ""
                generator.generate_erf32(
                    target_file_name,
                    log_file_name,
                    error_counter,
                    datatype,
                    status,
                    user,
                )

                # Log missing stations.
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

            # For next iteration.
            year_int += 1
        # Finished.
        logger.info("")
        logger.info("=== Finished: " + str(config_file))

    def setup_logging(self, log_file_name):
        """ """
        # Remove old logfile, if exists.
        logfile_path = pathlib.Path(log_file_name)
        if logfile_path.exists():
            logfile_path.unlink()
        # New logfile, and console logging.
        logger = logging.getLogger("erf32_generator")
        logger.setLevel(logging.DEBUG)
        # Remove old handlers.
        while logger.hasHandlers():
            logger.removeHandler(logger.handlers[0])
        # To a log file named similar to produced xml file.
        file_handler = logging.FileHandler(log_file_name)
        file_handler.setLevel(logging.DEBUG)
        # Console logging.
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        # Create formatter and add to the handlers.
        formatter = logging.Formatter("%(asctime)s %(levelname)s : %(message)s")
        file_handler.setFormatter(formatter)
        formatter = logging.Formatter("%(message)s")
        console_handler.setFormatter(formatter)
        # Add filter to console to avoid huge error lists.
        class ConsoleFilter(logging.Filter):
            def filter(self, record):
                # return record.levelno in [logging.INFO, logging.WARNING]
                return record.levelno in [logging.DEBUG, logging.INFO, logging.WARNING]

        console_handler.addFilter(ConsoleFilter())
        # Add handlers to the loggers.
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)


# MAIN.
if __name__ == "__main__":
    """ """
    config_files = [
        # "erf32_config/ices_erf32_zooplankton.yaml",
        # "erf32_config/ices_erf32_zoobenthos.yaml",
        "erf32_config/ices_erf32_phytoplankton.yaml",
        # "erf32_config/ices_erf32_phytobenthos.yaml",
    ]
    generator = IcesErf32Generator()
    for config_file in config_files:
        generator.generate_erf32(config_file)
