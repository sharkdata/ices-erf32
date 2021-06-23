#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import logging
import erf32_generator


class IcesErf32Generator():
    """ """
    def __init__(self):
        """ """

    def generate_erf32(self, config_file):
        """ """
        # Config and metadata content.
        ices_config = erf32_generator.GeneratorConfig(config_file)
        ices_config.load_config()

        # Setup logging.
        log_file_name = ices_config.target_logfile_template
        log_file_name = log_file_name.replace("<", "")
        log_file_name = log_file_name.replace(">", "")

        logger = logging.getLogger('erf32_generator')
        self.setup_logging(log_file_name)

        print("")
        print("")
        logger.info("")
        logger.info("=== Processing: " + str(config_file))
        logger.info("")
        logger.info("Files to process: ")
        for source_file in ices_config.source_files:
            logger.info("- " + source_file)

        # Prepare data.
        logger.info("")
        logger.info("=== Preparing data ===")
        filters = erf32_generator.Erf32Filters(ices_config.filters_files)
        translate = erf32_generator.Erf32Translate(ices_config.translate_files)
        source_data = erf32_generator.Erf32DataShark(ices_config, filters, translate)
        for dataset_filepath in ices_config.source_files:
            source_data.add_shark_dataset(dataset_filepath)
        # Data result.
        data_rows = source_data.get_data_rows()
        logger.info("")
        logger.info("Total number of data rows: " + str(len(data_rows)))

        logger.info("")
        logger.info("=== Generate ICES ERF32 ===")
        generator = erf32_generator.GenerateIcesErf32(ices_config)
        generator.setup(data_rows)
        generator.generate_erf32_files()

        logger.info("")
        logger.info("=== Finished: " + str(config_file))

    def setup_logging(self, log_file_name):
        """ """
        # Remove old logfile, if exists.
        logfile_path = pathlib.Path(log_file_name)
        if logfile_path.exists():
            logfile_path.unlink()
        # New logfile, and console logging.
        logger = logging.getLogger('erf32_generator')
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
        formatter = logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
        file_handler.setFormatter(formatter)
        formatter = logging.Formatter('%(message)s')
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
        "erf32_config/ices_erf32_zooplankton.yaml",
        "erf32_config/ices_erf32_zoobenthos.yaml",
        "erf32_config/ices_erf32_phytoplankton.yaml",
        "erf32_config/ices_erf32_phytobenthos.yaml",
    ]
    generator = IcesErf32Generator()
    for config_file in config_files:
        generator.generate_erf32(config_file)
