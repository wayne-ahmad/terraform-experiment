import shutil
import boto3
import logging
import os
import json
import csv
from datetime import datetime
from dataquery_processor import _config
from dataquery_processor.pathutils import sanitise_filename

logger = logging.getLogger(__name__)

"""
Module for handling storage abstraction
"""


class DateTimeEncoder(json.JSONEncoder):
    """
    Handler for datetime objects in JSON
    """

    def default(self, z):
        if isinstance(z, datetime):
            return (str(z))
        else:
            return super().default(z)


class StorageController(object):
    """
    Factory and wrapper for obtaining StorageController instances
    """

    def __init__(self, output_type=None, client='', order_reference='', customer_reference=''):

        self.output_type = _config.get_output_type()

        if output_type == 's3' or (output_type is None and self.output_type == 's3'):
            self.controller = S3StorageController(client=client, order_reference=order_reference,
                                                  customer_reference=customer_reference)
        else:
            # Default
            self.controller = FileStorageController(client, order_reference=order_reference,
                                                    customer_reference=customer_reference)

    def store_object_as_json(self, filename, json_object):
        self.controller.store_object_as_json(filename, json_object)

    def store_object_as_csv(self, filename, object_to_store, headers=None):
        self.controller.store_object_as_csv(filename, object_to_store, headers=headers)

    def store_object_as_text(self, filename, object_to_store):
        self.controller.store_object_as_text(filename, object_to_store)

    def store_object(self, filename, object_to_store):
        self.controller.store_object(filename, object_to_store)

    def store_file(self, filename, file_to_store):
        self.controller.store_file(filename, file_to_store)

    def rollback(self):
        self.controller.rollback()

    def get_resource_path(self, filename=None):
        return self.controller.get_resource_path(filename=filename)

    def get_output_path(self, filename=None):
        return self.controller.get_output_path(filename=filename)


class S3StorageController(object):

    def __init__(self, client=None, order_reference='', customer_reference=''):
        self.config = _config.get_storage_configuration()
        if 'profile' in self.config and self.config['profile'] != '':
            session = boto3.Session(profile_name=self.config['profile'])
        else:
            session = boto3.Session()
        self.s3client = session.client('s3', region_name=self.config['region'])
        self.bucket = self.config['bucket']
        self.subfolder = self.config['subfolder']
        self.client = client
        self.order_reference = order_reference
        self.customer_reference = customer_reference
        self.resource_path = create_resource_path(self.order_reference, customer_reference=self.customer_reference)
        self.output_path = create_output_path(self.client, self.resource_path)

    def store_object(self, resource_name, path):
        resource_name = self.client + os.sep + resource_name
        try:
            self.s3client.upload_file(path, self.bucket,self.subfolder, resource_name)

        except Exception as e:
            logger.error("Error saving object in S3")
            raise e

    def store_object_as_text(self, filename, object_to_store):
        resource_name = self.get_resource_path(filename=filename)
        temp_file_path = '/tmp' + os.sep + filename
        store_text_file(temp_file_path, object_to_store)
        self.store_object(resource_name, temp_file_path)

    def store_object_as_json(self, filename, json_object):
        resource_name = self.get_resource_path(filename=filename)
        temp_file_path = '/tmp' + os.sep + filename
        store_json_file(temp_file_path, json_object)
        self.store_object(resource_name, temp_file_path)

    def store_object_as_csv(self, filename, object_to_store, headers=None):
        resource_name = self.get_resource_path(filename=filename)
        temp_file_path = '/tmp' + os.sep + filename
        store_csv_file(temp_file_path, object_to_store, headers)
        self.store_object(resource_name, temp_file_path)

    def rollback(self):
        pass

    def store_file(self, filename, file_to_store):
        resource_name = self.get_resource_path(filename)
        self.store_object(resource_name, file_to_store)

    def get_resource_path(self, filename=None):
        if filename is None:
            return self.resource_path
        else:
            return self.resource_path + os.sep + filename

    def get_output_path(self, filename=None):
        if filename is None:
            return self.output_path
        else:
            return self.output_path + os.sep + self.resource_path + os.sep + filename


class FileStorageController(object):

    def __init__(self, client, order_reference='', customer_reference=''):
        self.client = client
        self.order_reference = order_reference
        self.customer_reference = customer_reference
        self.resource_path = create_resource_path(self.order_reference, customer_reference=self.customer_reference)
        self.output_path = create_output_path(self.client, self.resource_path)

        try:
            self.__create_folder__()
        except Exception as e:
            self.completed = False
            self.in_progress = False
            logger.error("Could not create an output folder. This may be because the order already ran")
            logger.debug(e)
            raise e

    def store_object(self, filename, object_to_store):
        filename = self.get_output_path() + os.sep + filename
        with open(filename, "w", encoding='utf-8') as file:
            file.write(object_to_store)

    def store_file(self, filename, file_to_store):
        filename = self.get_output_path() + os.sep + filename
        shutil.move(file_to_store, filename)

    def store_object_as_csv(self, filename, object_to_store, headers=None):
        path = self.get_output_path() + os.sep + filename
        store_csv_file(path, object_to_store, headers)

    def store_object_as_json(self, filename, object_to_store):
        filename = self.get_output_path() + os.sep + filename
        store_json_file(filename, object_to_store)

    def store_object_as_text(self, filename, object_to_store):
        self.store_object(filename, object_to_store)

    def rollback(self):
        """
        Deletes all files and folders created by a failed processing attempt
        :return: None
        """
        print("rollback called")
        if os.path.exists(self.output_path):
            if os.path.exists(self.output_path + os.sep + "query.sql"):
                os.remove(self.output_path + os.sep + "query.sql")
            if os.path.exists(self.output_path + os.sep + "data.csv"):
                os.remove(self.output_path + os.sep + "data.csv")
            if os.path.exists(self.output_path + os.sep + "manifest.json"):
                os.remove(self.output_path + os.sep + "manifest.json")
            os.rmdir(self.output_path)

    def __create_folder__(self):
        """
        Creates the output folder for the order using the Order Reference.
        If a folder already exists, raises ValueError - possibly the order has
        already run once, or the reference is being reused.
        :return: path to the output folder
        """
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        else:
            logger.error("An output folder already exists for this order reference:" + self.output_path)
            raise ValueError("An output folder already exists for this order reference.")

    def get_resource_path(self, filename=None):
        if filename is None:
            return self.resource_path
        else:
            return self.resource_path + os.sep + filename

    def get_output_path(self, filename=None):
        if filename is None:
            return self.output_path
        else:
            return self.output_path + os.sep + filename


def store_text_file(filename, object_to_store):
    with open(filename, "w", encoding='utf-8') as file:
        output = object_to_store
        file.write(output)


def store_json_file(filename, object_to_store):
    """
    Generic method to locally store a JSON file
    :param filename:
    :param object_to_store:
    :return:
    """
    with open(filename, "w", encoding='utf-8') as file:
        output = json.dumps(object_to_store, cls=DateTimeEncoder, indent=4, separators=(", ", ": "), sort_keys=True)
        file.write(output)


def store_csv_file(filename, object_to_store, headers):
    """
    Generic method to locally store a CSV file
    :param filename: the name of the file to store
    :param object_to_store: the data as a list
    :param headers: a list of column headers
    :return:
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(headers)  # column headers
        for row in object_to_store:
            writer.writerow(row)


def create_output_path(client, resource_path):
    """
    Generates a path for output using the Client ID, Order Reference and (optionally) a Customer Reference.
    :return: the output path component
    """
    base_path = _config.get_output_path()
    client_id = sanitise_filename(client)
    output_path = base_path + os.sep + client_id + os.sep + resource_path
    return output_path


def create_resource_path(order_reference, customer_reference=None):
    """
    Generates a path for output using the Order Reference and (optionally) a Customer Reference.
    :return: the output path component
    """
    date_part = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    try:
        order_ref = sanitise_filename(order_reference)
    except ValueError:
        logger.warning("No order reference provided")
        order_ref = 'NoOrderReference'

    if customer_reference is not None and customer_reference.strip() != "":
        customer_ref = sanitise_filename(customer_reference)
        resource_path = date_part + '-' + order_ref + '-' + customer_ref
    else:
        resource_path = date_part + '-' + order_ref

    return resource_path
