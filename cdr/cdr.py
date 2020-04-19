import os

import boto3
from progressbar import progressbar

from cdr.constants import CDR_TYPES, RESULTS, ABANDON, STANDARD_FIELDS, QUEUE_FIELDS
from cdr.cdr_parser import CDRParser
from cdr.csv_cdr_parser import CSVCDRParser
from cdr.sqlite_cdr_parser import SqliteCDRParser
from cdr.elasticsearch_cdr_parser import ElasticsearchCDRParser

class cdr(CDRParser):
    def __init__(self, 
        s3=None,
        bucket_name=None,
        folder_prefix=None,
        cdr_folder=None,
        debug=False
    ):
        super().__init__(cdr_folder=cdr_folder)
        self.s3 = s3 or boto3.resource('s3')
        self.bucket_name = bucket_name or os.environ.get('BUCKET_NAME')
        self.folder_prefix = folder_prefix or os.environ.get('FOLDER_PREFIX')
        self.s3_client = self.s3.meta.client
        self.bucket = self.s3.Bucket(self.bucket_name)
        if debug is True:
            boto3.set_stream_logger(name='botocore')

    @property
    def marker(self):
        marker = os.environ.get('CDR_MARKER', None)
        if marker is None or marker == '':
            marker = sorted(os.listdir(self.cdr_folder), reverse=True)[0]
        return self.folder_prefix + marker

    def get_last_modified(self, obj):
        return obj.last_modified
    
    def download_latests_cdr(self, object_prefix=''):
        prefix = self.folder_prefix + object_prefix
        print(f"Looking for new CDRs from:\n{self.marker}\n")
        cdr_objects = self.bucket.objects.filter(
            Prefix=prefix, MaxKeys=1000, Marker=self.marker)
        sorted_cdr_objects = sorted(cdr_objects, key=self.get_last_modified, reverse=True)
        if len(sorted_cdr_objects) is 0:
            print("No new CDRs to download")
            return
        for cdr_object in progressbar(sorted_cdr_objects):
            key = cdr_object.key
            filepath = f"{self.cdr_folder}/{key.replace(self.folder_prefix, '')}"
            self.s3_client.download_file(self.bucket_name, key, filepath)   

    def process_cdr(self, target='csv'):
        print('Processing CDR files:')
        if target == 'csv':
            parser = CSVCDRParser
        if target == 'sqlite':
            parser = SqliteCDRParser
        if target == 'elasticsearch':
            parser = ElasticsearchCDRParser
        if parser is None:
            print(f'No parser available for provided target: {target}')
            return
        parser(cdr_folder=self.cdr_folder).parse()