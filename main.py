"""api-deploy

Despliega un producto en un manager de API Connect 2018
"""

import os
import sys
import oyaml as yaml
import json
import logging
import requests
# import argparse

from pyapic import APIConnect

# Hide SSL verify warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class APIDeployError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


__author__ = "Jesús Moreno Amor"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Jesús Moreno Amor"
__email__ = "jesus@morenoamor.com"
__status__ = "Production"


def load_yaml(filename, encoding='utf-8'):
    with open(filename, 'r', encoding=encoding) as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as ex:
            raise APIDeployError("Error al cargar el archivo: " + filename, None)


def publish(product_file, organization, catalog, space):
    """Publish a product to a catalog"""

    # Load the product
    product = load_yaml(product_file)

    # This will hold the files to upload to publish the product
    files = []

    # Loop through the product APIs to get the files that will be uploaded
    for name, api_definition in product['apis'].items():
        if "name" in api_definition.keys():
            '''
            If the API is defined by name and version, we need to search through the filesystem
            for a yaml fil that contains the API and version specified
            '''
            pass
        if "$ref" in api_definition.keys():
            logger.debug(f"API $ref {api_definition['$ref']}")
            '''
            If the API is defined as a external reference, we need to solve it and transform the
            definition from:
                $ref: resourceconfigurationrest.yaml
            to:
                name: 'resourceconfigurationrest:1.1'
            '''
            product_path = os.path.dirname(product_file)

            # Clean the API reference name, solo para VODAFONE
            clean_name = api_definition['$ref'].split('_')[0] + ".yaml"
            logger.debug(f"Cleaned {api_definition['$ref']} to {clean_name}")

            # Load the API
            api_filename = os.path.join(product_path, clean_name)
            api = load_yaml(api_filename, encoding='utf-8')

            # Transform the reference from $ref to name
            api_definition['name'] = f"{api['info']['x-ibm-name']}:{api['info']['version']}"
            logger.debug(f"Translated {api_definition['$ref']} to {api_definition['name']}")
            del api_definition['$ref']

            # Add the API file to the publish order
            files.append(
                ('openapi', ('openapi', open(api_filename, 'rb'), 'application/yaml'))
            )
            logger.info(f"Added API {api_filename} to the publish order")

            # If the API has a WSDL definition, add it to the publish order
            if api['x-ibm-configuration']['type'] == "wsdl" and 'wsdl-definition' in api['x-ibm-configuration']:
                wsdl_filename = os.path.join(product_path, api['x-ibm-configuration']['wsdl-definition']['wsdl'])
                files.append(
                    ('wsdl', ('wsdl', open(wsdl_filename, 'rb'), 'application/zip'))
                )
                logger.info(f"Added WSDL {wsdl_filename} to the publish order")

    # Dump the product to a temporal file that doesn't have $ref references
    temporal_product = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'to_deploy.yaml')
    with open(temporal_product, 'w', encoding='utf-8') as stream:
        yaml.dump(product, stream)

    # Add the product file to the publish order
    files.append(
        ('product', ('product', open(temporal_product, 'rb'), 'application/yaml')),
    )
    logger.info(f"Added product {temporal_product} to the publish order")

    # Publish the product
    published_product = apic.product_publish(organization, catalog, product, files, space)

    return published_product


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
    # main()

    logger = logging.getLogger(__name__)

    product_file = os.getenv("PRODUCT_FILE")
    manager_host = os.getenv("MANAGER_HOST", "localhost:2000")
    manager_usrname = os.getenv("MANAGER_USRNAME")
    manager_password = os.getenv("MANAGER_PASSWORD")
    manager_realm = os.getenv("MANAGER_REALM")
    catalog = os.getenv("CATALOG", "sadbox")
    organization = os.getenv("CATALOG", "localtest")
    space = os.getenv("CATALOG", None)

    apic = APIConnect(manager=manager_host)
    apic.verify_ssl = False

    # Login
    apic.login(manager_usrname, manager_password, manager_realm)

    # Publish the product
    product = load_yaml(product_file)
    published_product = publish(product_file, organization, catalog, space)

    # Get product status
    product_version = product['info']['version']
    product_name = product['info']['name']
    product_b = apic.product_get(organization, catalog, product_name, product_version)
