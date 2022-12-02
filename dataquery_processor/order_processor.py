from datetime import datetime
import logging
from dataquery_processor import QueryBuilder, OdbcQueryRunner, OrderValidator, StorageController, ExcelHandler
from dataquery_processor import _config
logger = logging.getLogger(__name__)


class OrderProcessor(object):
    """
    Main workflow class - initialized with an order manifest, it then
    validates and processes the order in the manifest.
    """

    def __init__(self, order, config=_config):
        self.config = config
        self.order = order
        self.in_progress = True
        self.completed = False
        self.notices = None
        self.output_path = None
        self.resource_path = None
        self.storage_controller = None

    def process(self):
        """
        Main process method - calls all processing steps in sequence. If there
        are any problems encountered, these are logged and exceptions raised.
        :return: True if process completed
        """
        logger.info('processing order ' + self.order['orderRef'])

        #
        # Obtain a storage controller for storing the results - this could be for a local
        # file system, mounted file system, MongoDB document store, or Amazon S3 storage, for example.
        #
        try:
            self.__initialise_storage_controller__()
        except Exception as e:
            self.completed = False
            self.in_progress = False
            logger.error("Could not initialise storage")
            logger.debug(e)
            raise e

        try:
            self.__validate_order__()
            self.__generate_query__()
            self.__execute_query__()
            self.__write_receipt_manifest__()
            self.completed = True
            self.in_progress = False
            return True
        except Exception as e:
            self.storage_controller.rollback()
            self.completed = False
            self.in_progress = False
            logger.error("An error occurred during processing; the results have been rolled back.")
            logger.debug(e)
            raise e

    def __initialise_storage_controller__(self):
        """
        Sets up the storage controller for this object
        :return: None
        """
        customer_ref = None
        client_id = self.order['client']
        try:
            order_reference = self.order['orderRef']
        except ValueError:
            logger.warning("No order reference provided")
            order_reference = 'NoOrderReference'
        if 'customerRef' in self.order and self.order['customerRef'] is not None and self.order['customerRef'].strip() != "":
            customer_ref = self.order['customerRef']
        self.storage_controller = StorageController(client=client_id, order_reference=order_reference, customer_reference=customer_ref)

    def __validate_order__(self):
        """
        Validates that the order has a valid orderRef, is for a valid datasource, and that the contents
        match the metadata associated with it. Raises ValueError if any validation steps fail.
        Finally, runs rule processor and generates a set of notices for all warnings. If the rules processor
        finds an error - e.g. an order that requires IPO intervention - this also raises an exception
        :return: None
        """
        order_validator = OrderValidator(self.order)
        order_validator.validate_order()
        self.notices = order_validator.notices

    def __generate_query__(self):
        """
        Generates the query for the order
        :return: None
        """
        logger.info('generating query for order ' + self.order['orderRef'])
        self.query = QueryBuilder(self.order, config=self.config).create_query()
        self.storage_controller.store_object_as_text("query.sql", self.query[0])

    def __execute_query__(self):
        """
        Executes the generated query
        :return: None
        """
        logger.info('executing query for order ' + self.order['orderRef'])
        logger.debug("SQL = " + self.query[0])
        logger.debug("Parameters = " + ','.join(self.query[1]))
        runner = OdbcQueryRunner(config=self.config)

        # Create a temp CSV file
        runner.run_query_and_save_results(query=self.query, file_name="/tmp/data.csv")

        # Build Excel versions
        excel_handler = ExcelHandler(manifest=self.order, output_file='/tmp/pivot.xlsx', csv_file="/tmp/data.csv")
        excel_handler.create_workbook()
        self.storage_controller.store_file(filename='pivot.xlsx', file_to_store='/tmp/pivot.xlsx')
        excel_handler.create_notes_only('/tmp/notes.xlsx')
        self.storage_controller.store_file(filename='notes.xlsx', file_to_store='/tmp/notes.xlsx')

        # Store the CSV
        self.storage_controller.store_file(filename='data.csv', file_to_store='/tmp/data.csv')

        # Save the filename
        self.output_filename = self.storage_controller.get_resource_path("data.csv")

        # Add completion stamp
        self.job_completed = datetime.now()

    def __write_receipt_manifest__(self):
        """
        Writes the manifest with a completion timestamp and output file name
        to the configured storage system, and also uploads a copy to S3.
        :return: None
        """
        logger.info('writing manifest for order ' + self.order['orderRef'])

        manifest = self.order
        manifest['outputFile'] = self.output_filename
        manifest['jobCompleted'] = self.job_completed
        self.storage_controller.store_object_as_json(filename="manifest.json", json_object=self.order)

        # Upload to S3 if we aren't using S3 storage already
        if _config.get_output_type() != 's3' and _config.get_output_manifests_to_s3():
            customer_ref = None
            client_id = self.order['client']
            order_reference = self.order['orderRef']
            if 'customerRef' in self.order and self.order['customerRef'] is not None and self.order['customerRef'].strip() != "":
                customer_ref = self.order['customerRef']
            s3_storage_controller = StorageController(output_type='s3', client=client_id, order_reference=order_reference, customer_reference=customer_ref)
            s3_storage_controller.store_object_as_json('manifest.json', json_object=self.order)




