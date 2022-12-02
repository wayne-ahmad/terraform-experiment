import logging

from pypika import Table, Criterion, MSSQLQuery as Query, functions as fn, Parameter
from dataquery_processor import _config
logger = logging.getLogger(__name__)


class QueryBuilder(object):
    """
    Class for building SQL queries from a request manifest
    """

    def __init__(self, manifest, config=_config):
        self.config = config
        self.years = manifest['years']
        self.fieldnames = []
        self.constraints = []
        self.parameters = []
        self.onward_use_category = manifest['onwardUseCategory']
        self.map_fields_and_constraints(manifest['items'])
        self.measure = self.map_measure(manifest['measure'])
        self.table = Table(self.map_table(manifest['datasource']), schema='dbo')
        logger.debug("Query builder using table " + str(self.table))

    def map_fields_and_constraints(self, items):
        """
        Maps the items in a request into columns and constraints and store
        in object properties
        :param items: the array of items in the request
        :return: None
        """
        for item in items:
            item['fieldName'] = self.map_column(item['fieldName'])
            if 'allowedValues' in item.keys() and len(item['allowedValues']) > 0:
                self.constraints.append(item)
            else:
                self.fieldnames.append(item['fieldName'])

    def map_table(self, table):
        return self.config.get_table_mapping(table)

    def map_measure(self, measure):
        return self.config.get_measure_mapping(measure)

    def map_column(self, column):
        return self.config.get_column_mapping(column)

    def create_query(self):
        """
        Constructs the query by combining the selections and constraints.
        :return: an array containing the query prepared statement, and the parameters
        """
        select_fields = self.fieldnames.copy()
        select_fields.append(fn.Sum(self.table[self.measure], self.measure))
        q = Query().\
            from_(self.table).\
            select(*select_fields).\
            groupby(*self.fieldnames)

        q = self.create_constraints(q)

        return [q.get_sql(), self.parameters]

    def create_constraints(self, q):
        """
        Builds a set of constraints from the query; this consists of both
        defined constraints, and the implicit constraint on years. Uses the
        'in' method for determining constraint syntax
        :param q: the Query object
        :return: the Query object with constraints
        """
        clauses = []
        for constraint in self.constraints:
            column = constraint['fieldName']
            self.parameters.extend(constraint['allowedValues'])
            placeholders = []
            for i in range(len(constraint['allowedValues'])):
                placeholders.append(Parameter('?'))
            clauses.append(self.table[column].isin(placeholders))

        clauses.append(self.table['Onward use category '+self.onward_use_category] == 1)

        #
        # For years, querying on year start is much faster
        #
        clauses.append(self.table['Academic year start'].isin(self.get_year_starts()))
        q = q.where(Criterion.all(clauses))
        return q

    def get_year_starts(self):
        """
        Converts the array of academic year strings for a request into an array of year start integers
        :return: an array of integers for each year start
        """
        year_starts = []
        for year in self.years:
            year_start = int(year.split('/')[0])
            year_starts.append(year_start)
        return year_starts
