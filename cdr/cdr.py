import os
import queue
import threading

import boto3
from progressbar import progressbar, ProgressBar

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
        num_worker_threads=10,
        debug=False
    ):
        super().__init__(cdr_folder=cdr_folder)
        self.s3 = s3 or boto3.resource('s3')
        self.bucket_name = bucket_name or os.environ.get('BUCKET_NAME')
        self.folder_prefix = folder_prefix or os.environ.get('FOLDER_PREFIX')
        self.num_worker_threads = num_worker_threads
        self.s3_client = self.s3.meta.client
        self.bucket = self.s3.Bucket(self.bucket_name)
        if debug is True:
            boto3.set_stream_logger(name='botocore')

    @property
    def marker(self):
        marker = os.environ.get('CDR_MARKER', None)
        if marker is None or marker == '':
            try:
                marker = sorted(os.listdir(self.cdr_folder), reverse=True)[0]
            except Exception:
                marker = ''
        return self.folder_prefix + marker

    def get_last_modified(self, obj):
        return obj.last_modified

    def create_worker(self, task):
        def worker():
            while True:
                item = self.q.get()
                if item is None:
                    break
                task(item)
                self.q.task_done()
        return worker

    def download_cdr(self, item):
        (index, key) = item
        filepath = f"{self.cdr_folder}/{key.replace(self.folder_prefix, '')}"
        self.s3_client.download_file(self.bucket_name, key, filepath)
        try:
            self._bar.update(index)
        except:
            print('Can\'t update the progressbar')
    
    def download_latests_cdr(self, object_prefix=''):
        prefix = self.folder_prefix + object_prefix
        print(f"Looking for new CDRs starting from: {self.marker}. With prefix: {prefix}")
        cdr_objects = self.bucket.objects.filter(
            Prefix=prefix, MaxKeys=1000, Marker=self.marker)
        sorted_cdr_objects = sorted(cdr_objects, key=self.get_last_modified, reverse=True)
        if len(sorted_cdr_objects) is 0:
            print("No new CDRs to download")
            return
        print('Gathered all cdr objects. Proceeding to download...')
        # Wrap everything into a ProgressBar Context
        with ProgressBar(max_value=len(sorted_cdr_objects)) as bar:
            # Store progressbar into class variable
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
            # Put keys into queue
            for index, cdr_object in enumerate(sorted_cdr_objects):
                self.q.put((index, cdr_object.key,))
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