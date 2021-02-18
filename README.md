# ICES ERF 3.2 Generator

Generator for the ICES ERF 3.2 format.

## Usage

The ICES Environmental Reporting Format (ERF 3.2) is used to report environmental data to ICES.

## Installation

Python3, venv and git must be installed.

    # Linux:
    git clone https://github.com/sharkdata/ices-erf32.git
    cd ices-erf32
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Windows (with example path to Python).
    git clone https://github.com/sharkdata/ices-erf32.git
    cd ices-erf32
    C:\Python39\python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

## Development

    python3 ices_erf32_generator_main.py

## Run from the command line

    # Go to directory:
    cd ices-erf32

    # Activate the virtual environment for Python:
    source venv/bin/activate # Linux.
    venv\Scripts\activate # Windows.
    
    # Run the generator in Command Line Interface (CLI) mode:
    python3 ices_erf32_generator_cli.py

## Contact

shark@smhi.se
