import logging

from dataquery_processor import OrderProcessor, QueueController
from dataquery_processor.queue_controller import Message

logger = logging.getLogger()

# lambda handler

def lambda_handler(event, context):
    if 'Records' in event:
        records = event['Records']
        for record in records:
            message = Message(record)
            proc = OrderProcessor(message.order())
            try:
                proc.process()
                logger.info("Job completed. Deleting message from queue")
                q = QueueController()
                q.delete_message(message)
            except Exception as e:
                logger.error("Job was not completed successfully; leaving message on queue")
                raise e
