import os
import configparser
from dataquery_processor.pathutils import get_config_path

CONFIG_FILE = 'config.ini'
DEFAULT_OUTPUT_PATH = 'output'

FILE_OUTPUT = 'file'
S3_OUTPUT = 's3'
DEFAULT_OUTPUT_TYPE = FILE_OUTPUT


class Config:
    """
    Utility class for accessing configuration settings.
    """

    def __init__(self, config_file_name=CONFIG_FILE):
        path = get_config_path(config_file_name)
        self.config = configparser.ConfigParser()
        self.config.read(path, encoding='utf-8')
        self.conn = self.config.get("ODBC", "conn")
        self.order_batch_size = 1
        if self.config.has_option('default', "order_batch_size"):
            self.order_batch_size = self.config.getint("default", "order_batch_size")

        self.queue_configuration = {"profile": self.config.get('sqs', "profile"),
                                    "queue": self.config.get('sqs', "queue"),
                                    "region": self.config.get('sqs', "region")}
        self.queue_configuration["queue"] = os.environ.get("ORDER_QUEUE", self.queue_configuration["queue"])

        self.storage_configuration = {"profile": self.config.get('s3', "profile"),
                                      "bucket": self.config.get('s3', "bucket"),
                                      "region": self.config.get('s3', "region")}
        self.storage_configuration["bucket"] = os.environ.get("PROCESSED_ORDERS_BUCKET", self.storage_configuration["bucket"])

    def get_table_mapping(self, mapping):
        if self.config.has_option('table_mappings', mapping):
            return self.config.get('table_mappings', mapping)

    def get_measure_mapping(self, mapping):
        return self.config.get('measure_mappings', mapping)

    def get_column_mapping(self, column):
        if self.config.has_option('column_mappings', column):
            return self.config.get('column_mappings', column)
        return column

    def get_queue_configuration(self):
        return self.queue_configuration

    def get_storage_configuration(self):
        return self.storage_configuration

    def get_mapped_metadata_path(self, datasource_name):
        if self.config.has_option("datasource_mappings", datasource_name):
            return self.config.get("datasource_mappings", datasource_name)

    def get_output_path(self):
        if self.config.has_option("output", "output_path"):
            return self.config.get("output", "output_path")
        else:
            return DEFAULT_OUTPUT_PATH

    def get_output_type(self):
        if self.config.has_option("output", "output_type"):
            return self.config.get("output", "output_type")
        else:
            return DEFAULT_OUTPUT_TYPE

    def get_output_manifests_to_s3(self):
        if self.config.has_option("output", "output_manifest_to_s3"):
            return self.config.getboolean("output", "output_manifest_to_s3")
        else:
            return True


_config = Config()
