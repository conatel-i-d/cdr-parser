import requests

from cdr.cdr_parser import CDRParser
from cdr.constants import STANDARD_FIELDS, QUEUE_FIELDS

class ElasticsearchCDRParser(CDRParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elasticsearch_url = kwargs.get('elasticsearch_url', 'http://localhost:9200')
        self.elasticsearch_type = kwargs.get('elasticsearch_type', 'cdr')

    def write_line_to_elasticsearch(self, line, report):
        if report is None:
            return
        if report is 'standard':
            self.post_line(line, 'standard', STANDARD_FIELDS)
        if report is 'queue':
            self.post_line(line, 'queue', QUEUE_FIELDS)

    def post_line(self, line, index, fields):
        url = f'{self.elasticsearch_url}/{index}/{self.elasticsearch_type}'
        response = requests.post(url, json=self.line_to_dict(line, ))    

    def line_to_dict(self, line, fields):
        line_dict = {}
        for index, field in enumerate(fields):
            line_dict[field] = line[index]
        return line_dict

    def parse(self):
        self.process_files(self.write_line_to_elasticsearch)