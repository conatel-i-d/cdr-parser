import os
import csv

from cdr.cdr_parser import CDRParser
from cdr.constants import STANDARD_FIELDS, QUEUE_FIELDS

class CSVCDRParser(CDRParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.standard_csv_path = kwargs.get('standard_csv_path', './standard.csv')
        self.queue_csv_path = kwargs.get('queue_csv_path', './queue.csv')

    def delete_csv_files(self):
        print('Deleting reports...')
        for report in [self.standard_csv_path, self.queue_csv_path]:
            if os.path.exists(report):
                os.remove(report)
            else:
                print(f'Report {report} not found. Continuing...')
                continue

    def write_line_to_csv(self, line, report, **kwargs):
        csv_file = kwargs.get(report, None)
        if csv_file is None:
            return
        csv_file.write(','.join(list(map(lambda x: str(x), line))))
        csv_file.write('\n')

    def parse(self, **kwargs):
        if kwargs.get('clean', False) is True:
            self.delete_csv_files()
        with open(self.standard_csv_path, 'a') as sr, open(self.queue_csv_path, 'a') as qr:
            sr.write(",".join(STANDARD_FIELDS))
            sr.write("\n")
            qr.write(",".join(QUEUE_FIELDS))
            qr.write("\n")
            print('Generating CSV files...\n')
            self.process_files(self.write_line_to_csv, standard=sr, queue=qr)