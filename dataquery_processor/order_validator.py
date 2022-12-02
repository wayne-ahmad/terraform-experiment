import logging
from metadata_rules import check_rules, FAILURE, map_item
from dataquery_processor.pathutils import sanitise_filename
from metadata_specifications import get_data_source

logger = logging.getLogger(__name__)


class OrderValidator(object):
    """
    Validates that order manifests contain valid information.
    """

    def __init__(self, order):
        self.order = order
        self.notices = None
        self.metadata = None

    def validate_constraints(self):
        """
        Validates any constraints on an item, raising ValueError where invalid.
        Note that we only validate constraints where there is a value domain to
        check against - we don't validate input against 'free text' such as
        course title fields etc.
        :return: None
        """
        for item in self.order['items']:
            field = map_item(item, self.metadata)
            if 'allowedValues' in item and 'domain' in field:
                for constraint in item['allowedValues']:
                    if constraint not in field['domain']:
                        raise ValueError("Constraint is not in domain of field")

    def validate_order(self):
        """
        Validates that the order has a valid orderRef, is for a valid datasource, and that the contents
        match the metadata associated with it. Raises ValueError if any validation steps fail.
        Finally, runs rule processor and generates a set of notices for all warnings. If the rules processor
        finds an error - e.g. an order that requires IPO intervention - this also raises an exception
        :return: None
        """

        if 'orderRef' not in self.order or self.order['orderRef'] is None:
            logger.error("There is no order reference for the order")
            raise ValueError("There is no order reference for the order")

        self.order['orderRef'] = str(self.order['orderRef'])

        if self.order['orderRef'].strip() == '':
            logger.error("There is no order reference for the order")
            raise ValueError("There is no order reference for the order")

        try:
            sanitise_filename(self.order['orderRef'])
        except Exception:
            logger.error("The order reference provided is invalid")
            raise ValueError("The order reference provided is invalid")

        if 'datasource' not in self.order or self.order['datasource'] is None:
            logger.error("There is no data source specified for the order")
            raise ValueError("There is no data source specified")

        metadata = get_data_source(self.order['datasource'])

        if metadata is None:
            logger.error("The data source in the manifest does not match a metadata specification")
            raise ValueError("The data source in the manifest does not match a metadata specification")

        try:
            self.metadata = metadata
            self.metadata = self.metadata['datasource']
        except Exception:
            logger.error("Metadata could not be loaded")
            raise ValueError("Metadata could not be loaded")

        if 'items' not in self.order or len(self.order['items']) == 0:
            logger.error("The order contains no items")
            raise ValueError("The order contains no items")

        self.notices = check_rules(self.metadata, self.order)
        for notice in self.notices:
            if notice.severity == FAILURE:
                logger.error("The order is invalid as it breaks one or more data rules")
                raise ValueError("The order is invalid as it breaks one or more data rules")

        self.validate_constraints()
