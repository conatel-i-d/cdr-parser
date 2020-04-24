import os
import queue
import threading
import traceback

import boto3
from progressbar import progressbar, ProgressBar
from datetime import datetime

from cdr.constants import CDR_TYPES, RESULTS, ABANDON, STANDARD_FIELDS, QUEUE_FIELDS
from cdr.cdr_parser import CDRParser
from cdr.csv_cdr_parser import CSVCDRParser
from cdr.sqlite_cdr_parser import SqliteCDRParser
from cdr.elasticsearch_cdr_parser import ElasticsearchCDRParser
from cdr.csv_splitter import split

class cdr(CDRParser):
    def __init__(self, 
        s3=None,
        bucket_name=None,
        folder_prefix=None,
        cdr_folder=None,
        downloaded_cdr_file=None,
        cdr_db=None,
        num_worker_threads=20,
        debug=False
    ):
        super().__init__(cdr_folder=cdr_folder)
        self.s3 = s3 or boto3.resource('s3')
        self.bucket_name = bucket_name or os.environ.get('BUCKET_NAME')
        self.folder_prefix = folder_prefix or os.environ.get('FOLDER_PREFIX')
        self.downloaded_cdr_file = downloaded_cdr_file or os.environ.get('DOWNLOADED_CDR_FILE')
        self.cdr_db = cdr_db or os.environ.get('CDR_DB')
        self.num_worker_threads = num_worker_threads
        self.s3_client = self.s3.meta.client
        self.bucket = self.s3.Bucket(self.bucket_name)
        if debug is True:
            boto3.set_stream_logger(name='botocore')

    @property
    def last_downloaded_cdr_key(self):
        try:
            with open(self.cdr_db, 'r') as db:
                return db.readline().rstrip('\n')
        except:
            return None

    def get_last_modified(self, obj):
        return obj.last_modified

    def get_datetime_from_key(self, key):
        filename = key[-29:]
        cdr_year = int(filename[:4])
        cdr_month = int(filename[4:6])
        cdr_day = int(filename[6:8])
        cdr_hour = int(filename[9:11])
        cdr_minute = int(filename[11:13])
        cdr_seconds = int(filename[13:15])
        return datetime(cdr_year, cdr_month, cdr_day, cdr_hour, cdr_minute, cdr_seconds)

    def sort_by_date(self, obj):
        current_datetime = self.get_datetime_from_key(obj.key)
        return current_datetime.timestamp()

    def create_worker(self, task):
        def worker():
            while True:
                item = self.q.get()
                if item is None:
                    break
                task(item)
                self.q.task_done()
        return worker

    def download_cdr(self, key):
        filepath = f"{self.cdr_folder}/{key.replace(self.folder_prefix, '')}"
        self.s3_client.download_file(self.bucket_name, key, filepath)
        try:
            self.update_progress_bar()
        except:
            print('Can\'t update the progressbar')

    def update_progress_bar(self):
        index = self._bar_index
        self._bar.update(index)
        self._bar_index += 1

    def download_latests_cdr(self):
        datetime_of_last_downloaded_cdr = self.get_datetime_from_key(self.last_downloaded_cdr_key)
        print('This is the datetime of the last downloaded CDR:', datetime_of_last_downloaded_cdr)
        print(f"Looking for new CDRs starting from: {self.last_downloaded_cdr_key}. With folder prefix: {self.folder_prefix}")
        cdr_objects = self.bucket.objects.filter(Prefix=self.folder_prefix, MaxKeys=1000, Marker=self.last_downloaded_cdr_key)
        objects_to_download = list(filter(lambda x: self.get_datetime_from_key(x.key) > datetime_of_last_downloaded_cdr, cdr_objects))
        sorted_objects_to_download = sorted(objects_to_download, key=self.sort_by_date, reverse=True)
        if len(sorted_objects_to_download) > 0:
            print('Cantidad de cdrs a descargar:', len(sorted_objects_to_download))
        else:
            print('No hay nuevos CDRs para descaragr')
            return
        print('Gathered all cdr objects. Proceeding to download...')
        # Try to download the new cdrs
        try:
            self.start_download_queue(sorted_objects_to_download)
            with open(self.cdr_db, 'w') as cdr_db:
                cdr_db.writelines([sorted_objects_to_download[0].key])
        except:
            print('Something went wrong')
            traceback.print_exc()

    def start_download_queue(self, cdr_objects):
        # Wrap everything into a ProgressBar Context
        with ProgressBar(max_value=len(cdr_objects)) as bar:
            # Store progressbar into class variable
            self._bar_index = 0
            self._bar = bar
            # Create a new queue
            self.q = queue.Queue()
            # Threads list
            threads = []
            # Create the target worker to be used
            target = self.create_worker(self.download_cdr)
            # Start each worker in a new thread
            for i in range(self.num_worker_threads):
                thread = threading.Thread(target=target)
                thread.start()
                threads.append(thread)
            # Put keys into queue and store it into the downloaded cdr file
            for cdr_object in cdr_objects:
                cdr_object_key = cdr_object.key 
                self.q.put(cdr_object_key)
            # Block until all tasks are done
            self.q.join()
            # Stop workers
            for i in range(self.num_worker_threads):
                self.q.put(None)
            # Close threads
            for thread in threads:
                thread.join() 
            
    def split_csv_report(self, report, row_limit=125000):
        report_basepath = report.replace('.csv', '')
        print(f'Spliting report: {report_basepath}')
        with open(report, 'r') as r:
            csvfile = r.readlines()
            headers = csvfile[0]
            split_index = 1
            for i in range(len(csvfile)):
                if i % row_limit == 0:
                    filepath = report_basepath + '_' + str(split_index) + '.csv'
                    print(filepath)
                    with open(filepath, 'w+') as f:
                        if split_index > 1:
                            f.write(headers)
                        f.writelines(csvfile[i:i+row_limit])
                        split_index += 1

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