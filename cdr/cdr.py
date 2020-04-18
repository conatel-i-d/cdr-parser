import os
import sys
import csv
import traceback
import sqlite3

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
        standard_csv_path='./standard.csv',
        queue_csv_path='./queue.csv',
        db_path='./db.sql'
    ):
        self.s3 = s3 or boto3.resource('s3')
        self.bucket_name = bucket_name or os.environ.get('BUCKET_NAME')
        self.folder_prefix = folder_prefix or os.environ.get('FOLDER_PREFIX')
        self.cdr_folder = cdr_folder or os.environ.get('CDR_FOLDER')
        self.standard_csv_path = standard_csv_path
        self.queue_csv_path = queue_csv_path
        self.db_path = db_path
        self.sqlite_conn = self.create_database()
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
            row[5][-32:],
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
            str(ABANDON.get(int(row[10]), '0')),
            row[11]
        ]

    def write_row_to_csvs(self, row, **kwargs):
        cdr_type = CDR_TYPES[row[1]]
        parse_method = getattr(self, cdr_type['method'], self.parse_pass)
        line = parse_method(row)
        report = kwargs.get(cdr_type['report'], None)
        if report is None:
            return
        report.write(','.join(line))
        report.write('\n')   
    
    def write_row_to_sqlite(self, row):
        cdr_type = CDR_TYPES[row[1]]
        parse_method = getattr(self, cdr_type['method'], self.parse_pass)
        line = parse_method(row)
        report = cdr_type['report']
        if report is None:
            return
        if report is 'standard':
            self.insert_line_in_standard_table(line)
        if report is 'queue':
            self.insert_line_in_queue_table(line)

    def insert_line_in_standard_table(self, line):
        sql = """
            INSERT INTO standard (
                switch_id,
                id,
                start_time,
                call_duration,
                origin,
                detination,
                result,
                osv_origin,
                osv_destination,
                pickup_time,
                hang_time,
                incoming_leg_pickup_time,
                incoming_leg_hang_time,
                outgoing_leg_pickup_time,
                outgoing_leg_hang_time
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        self.cursor.execute(sql, line)

    def insert_line_in_queue_table(self, line):
        sql = """
            INSERT INTO queue (
                id,
                time,
                queue_id,
                start_time,
                end_time,
                abandon,
                destination
            ) VALUES (?,?,?,?,?,?,?)
        """
        self.cursor.execute(sql, line)

    def process_files(self, row_processor, **kwargs):
        for file in progressbar(os.listdir(self.cdr_folder)):
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
                            row_processor(row, **kwargs)
                        except Exception as e:
                            print('Can\'t parse line:', sys.exc_info()[0])
                            traceback.print_exc()

    def process_cdr_to_csv(self):
        self.deletes()
        with open(self.standard_csv_path, 'a') as sr, open(self.queue_csv_path, 'a') as qr:
            self.process_files(self.write_row_to_csvs, standard=sr, queue=qr)

    def process_cdr_to_sqlite(self):
        self.process_files(self.write_row_to_sqlite)

    def process_cdr(self, target='csv'):
        print('Processing CDR files:\n')
        if target == 'sqlite':
            self.process_cdr_to_sqlite()
            return
        self.process_cdr_to_csv()

    def deletes(self):
        print('Deleting reports...')
        for report in [self.standard_csv_path, self.queue_csv_path]:
            if os.path.exists(report):
                os.remove(report)
            else:
                print(f'Report {report} not found. Continuing...')
                continue
        print('\n')

    def delete_database(self):
        print('Deleting database...')
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        else:
            print(f'Database file {self.db_path} not found. Continuing...')

    def create_database(self):
        self.delete_database()
        self.sqlite_conn = sqlite3.connect(self.db_path, isolation_level=None)
        self.cursor = self.sqlite_conn.cursor()
        # Create queue table
        self.cursor.execute('''
            CREATE TABLE queue (
                id text,
                time text,
                queue_id text,
                start_time text,
                end_time text,
                abandon integer,
                destination text
            );
        ''')
        # Create standard table
        self.cursor.execute('''
            CREATE TABLE standard (
                switch_id text,
                id text,
                start_time text,
                call_duration real,
                origin text,
                detination text,
                result text,
                osv_origin text,
                osv_destination text,
                pickup_time text,
                hang_time text,
                incoming_leg_pickup_time text,
                incoming_leg_hang_time text,
                outgoing_leg_pickup_time text,
                outgoing_leg_hang_time text 
            );
        ''')
        self.sqlite_conn.commit()