#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import erf32_generator


def generate_ices_erf32(config_file):
    """ """
    print("\n\n\n=== Processing: ", config_file)

    # Config and metadata content.
    ices_config = erf32_generator.GeneratorConfig(config_file)
    ices_config.load_config()

    # Prepare data.
    print("\n=== Preparing data ===")
    filters = erf32_generator.Erf32Filters(ices_config.filters_files)
    translate = erf32_generator.Erf32Translate(ices_config.translate_files)
    source_data = erf32_generator.Erf32DataShark(ices_config, filters, translate)
    for dataset_filepath in ices_config.source_files:
        source_data.add_shark_dataset(dataset_filepath)
    # Data result.
    data_rows = source_data.get_data_rows()
    print("DEBUG: Number of data rows", len(data_rows))

    print("\n=== Generate ICES ERF32 ===")
    generator = erf32_generator.GenerateIcesErf32(ices_config)
    generator.setup(data_rows)
    generator.generate_erf32_files()

    print("\n=== Finished: ", config_file)


# MAIN.
if __name__ == "__main__":
    """ """
    config_files = [
        "erf32_config/ices_erf32_zooplankton.yaml",
    ]
    for config_file in config_files:
        generate_ices_erf32(config_file)
