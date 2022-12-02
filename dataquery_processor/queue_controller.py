import boto3
import json
import logging
from dataquery_processor import _config
logger = logging.getLogger(__name__)


class Message(object):
    """
    Structure class for holding an SQS message object
    """

    def __init__(self, message):
        self.message = message

    def order(self):
        """
        Get the order (manifest) contained in the message
        :return: a manifest object
        """
        # Annoyingly, different cases are used by SQS in
        # API calls vs event triggers
        if 'Body' in self.message:
            body = self.message['Body']
        else:
            body = self.message['body']
        response = json.loads(body)
        payload = response['responsePayload']['order']
        return payload

    def receipt_handle(self):
        """
        Get the receipt handle for the message, so it can be deleted
        from the queue if successfully processed.
        :return:
        """
        # Annoyingly, different cases are used by SQS in
        # API calls vs event triggers
        if 'receiptHandle' in self.message:
            return self.message['receiptHandle']
        elif 'ReceiptHandle' in self.message:
            return self.message['ReceiptHandle']
        else:
            return None


class QueueController(object):
    """
    Wrapper class for an SQS queue
    """

    def __init__(self):
        """
        Create the instance using configuration supplied in config.ini
        """
        self.messages = []
        config = _config.get_queue_configuration()
        if 'profile' in config and config['profile'] != '':
            session = boto3.Session(profile_name=config['profile'])
        else:
            session = boto3.Session()
        self.sqsClient = session.client('sqs', region_name=config['region'])
        self.queue = config['queue']

        #
        # Load messages as soon as initialised
        #
        self.load_messages()

    def load_messages(self):
        """
        Loads messages from the queue
        :return:
        """
        logger.info("Loading manifests from queue")
        message_response = self.sqsClient.receive_message(
            QueueUrl=self.queue,
            MaxNumberOfMessages=_config.order_batch_size
        )
        if 'Messages' in message_response:
            self.messages = message_response['Messages']
            logger.info(str(len(self.messages)) + " manifests loaded")

    def read_message(self):
        if len(self.messages) > 0:
            return Message(self.messages.pop(0))
        else:
            return None

    def delete_message(self, message):
        if message.receipt_handle() is None:
            raise ValueError("No receipt handle for message - cannot delete")
        self.sqsClient.delete_message(
            QueueUrl=self.queue,
            ReceiptHandle=message.receipt_handle()
            )
        logger.info("deleted "+message.order()['orderRef'])
