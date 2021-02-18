#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2021-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import click
import ices_erf32_generator_main

global ices_config


@click.command()
@click.option(
    "--row",
    default=0,
    prompt="Execute row",
    help="Row number used to select which YAML-file to generate ICES-Erf32 from.",
)
def run_erf32_generator_command(row):
    """ """
    global ices_erf32_config
    if (row < 0) or (row > len(ices_erf32_config)):
        print("\n\nERROR: Wrong value. Please try again.\n\n")
        return
    if row == 0:
        for config_file in ices_erf32_config:
            ices_erf32_generator_main.generate_ices_erf32(config_file)
    else:
        ices_erf32_generator_main.generate_ices_erf32(ices_erf32_config[row - 1])


if __name__ == "__main__":
    """ """
    global ices_erf32_config
    ices_erf32_config = []
    for file_path in pathlib.Path("erf32_config").glob("ices_erf32_*.yaml"):
        ices_erf32_config.append(str(file_path))
    ices_erf32_config = sorted(ices_erf32_config)
    # Print before command.
    print("\n\nICES ERF 3.2 generator.")
    print("-----------------------------")
    print("Select row number. Press enter to run all.")
    print("Press Ctrl-C to terminate.\n")
    for index, row in enumerate(ices_erf32_config):
        print(index + 1, "  ", row)
    print("")
    # Execute command.
    run_erf32_generator_command()
