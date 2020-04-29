"""api-deploy

Despliega un producto en un manager de API Connect 2018
"""

import os
import sys
# import util
import oyaml as yaml
import json
import logging
import requests
import argparse

from pyapic import APIConnect


__author__ = "Jesús Moreno Amor"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Jesús Moreno Amor"
__email__ = "jesus@morenoamor.com"
__status__ = "Production"


def main():

    product_file = os.getenv("PRODUCT_FILE", "default")
    manager_host = os.getenv("MANAGER_HOST", "default")
    manager_usrname = os.getenv("MANAGER_USRNAME", "default")
    manager_password = os.getenv("MANAGER_PASSWORD", "default")
    manager_realm = os.getenv("MANAGER_REALM", "default")


    my_input = os.getenv("INPUT_MYINPUT", "default")

    my_output = f"Hello {my_input}"

    print(f"::set-output name=myOutput::{my_output}")


if __name__ == "__main__":
    main()
