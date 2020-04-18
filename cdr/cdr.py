import os
import sys
import csv
import traceback

import boto3
from progressbar import progressbar

from .dictionaries import CDR_TYPES, RESULTS, ABANDON

class cdr(object):
    def __init__(self, 
        s3=None,
        bucket_name=None,
        folder_prefix=None,
        cdr_folder=None,
        debug=False,
        standard_report_path='./standard_report.csv',
        queue_report_path='./queue_report.csv'
    ):
        self.s3 = s3 or boto3.resource('s3')
        self.bucket_name = bucket_name or os.environ.get('BUCKET_NAME')
        self.folder_prefix = folder_prefix or os.environ.get('FOLDER_PREFIX')
        self.cdr_folder = cdr_folder or os.environ.get('CDR_FOLDER')
        self.standard_report_path = standard_report_path
        self.queue_report_path = queue_report_path
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

    def parse_pass(self, row):
        pass

    def parse_standard(self, row):
        return [
            row[4],
            row[5][-32],
            row[2],
            row[3],
            row[11],
            row[10],
            RESULTS.get(row[17], 'NPI'),
            row[39],
            row[40],
            row[47],
            row[48],
            row[49],
            row[50],
            row[51],
            row[52]
        ]

    def parse_queue(self, row):
        return [
            row[4][-32:],
            row[2],
            row[6],
            row[7],
            row[8],
            ABANDON.get(int(row[10]), 'NPI'),
            row[11]
        ]

    def process_file(self, file, **kwargs):
        start_file = False
        end_file = False
        with open(f'{self.cdr_folder}/{file}', 'r') as csv_file:
            cdr_csv_file = csv.reader(csv_file, delimiter=',')
            for row in cdr_csv_file:
                if len(row) == 0:
                    continue
                if row[0][0:7] == 'CREATE:':
                    start_file = True
                    continue
                if row[0][0:6] == 'CLOSE:':
                    end_file = True
                    break
                if start_file and not end_file:
                    try:
                        cdr_type = CDR_TYPES[row[1]]
                        report = kwargs.get(cdr_type['report'], None)
                        if report is None:
                            continue
                        parse_method = getattr(self, cdr_type['method'], self.parse_pass)
                        line = parse_method(row)
                        report.write(','.join(line))
                        report.write('\n')
                    except Exception as e:
                        print('Can\'t parse line:', sys.exc_info()[0])
                        traceback.print_exc()

    def process_files(self, **kwargs):
        for file in progressbar(os.listdir(self.cdr_folder)):
            self.process_file(file, **kwargs)

    def process_cdr(self):
        print('Processing CDR files:\n')
        self.delete_reports()
        with open(self.standard_report_path, 'a') as sr, open(self.queue_report_path, 'a') as qr:
            self.process_files(standard_report=sr, queue_report=qr)
        print('\nDone!')

    def delete_reports(self):
        print('Deleting reports...\n')
        for report in [self.standard_report_path, self.queue_report_path]:
            if os.path.exists(report):
                os.remove(report)
            else:
                print(f'Report {report} not found. Continuing...')
                continue