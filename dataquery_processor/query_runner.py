import logging
import csv
import pyodbc  # Note this is included in a Lambda layer so is omitted from requirements.txt
from dataquery_processor import _config

logger = logging.getLogger(__name__)


class OdbcQueryRunner(object):
    """
    Creates a database connection and outputs the results.
    """

    def __init__(self, config=_config):
        """
        Create a query runner using the connection details
        from config.ini. Raises a pyODBC Error if connection fails.
        """
        self.config = config
        try:
            conn = pyodbc.connect(self.config.conn)
        except pyodbc.OperationalError as e:
            logger.error("Error connecting to database")
            raise e
        self.cursor = conn.cursor()

    def run_query_and_return_results(self, query):
        """
        Runs the query and returns a cursor for the result set that can
        be iterated over to obtain the data
        :param query: a query tuple containing a prepared statement and parameter list
        :return: a pyodbc cursor for the result set
        """
        return self.cursor.execute(query[0], query[1])

    def get_headers(self):
        """
        Returns the column headers from a cursor. Must be run after run_query_and_return_results.
        :return:
        """
        return [x[0] for x in self.cursor.description]

    def run_query_and_save_results(self, query=None, file_name=None):
        """
        Runs the query and outputs the results to a file
        :param query: a tuple containing the query and the parameters to run it with
        :param file_name: the file to save
        :return: None
        """
        logger.debug("Running query using ODBC")
        rows = self.run_query_and_return_results(query)
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(self.get_headers())  # column headers
            for row in rows:
                writer.writerow(row)
