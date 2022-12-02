import logging
import os
from dataquery_processor import get_config_path
from logging.config import fileConfig
from dataquery_processor import QueueController
from dataquery_processor import OrderProcessor

"""
Setup logging
"""
__package__ = 'dataquery_processor'
if os.path.exists(get_config_path('logging_config.ini')):
    fileConfig(get_config_path('logging_config.ini'), disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def main():
    """
    Main method and entry point for running a service locally.
    Loads configuration from file and initialises a QueueController instance.
    Runs controller once and exits.
    :return:
    """

    q = QueueController()
    if len(q.messages) == 0:
        logger.info("No new orders to process")
    while len(q.messages) > 0:
        message = q.read_message()
        if message:
            proc = OrderProcessor(message.order())
            if proc.process():
                logger.info("Job completed. Deleting message from queue")
                q.delete_message(message)
            else:
                logger.error("Job was not completed successfully; leaving message on queue")


if __name__ == "__main__":
    main()


def handler(event, context):
    main()
