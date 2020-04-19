import os
import csv
import sys
import traceback
from datetime import datetime

from progressbar import progressbar

from .constants import CDR_TYPES, RESULTS, ABANDON

class CDRParser(object):
    def __init__(self, cdr_folder=None):
        self.cdr_folder = cdr_folder or os.environ.get('CDR_FOLDER')
    
    def parse(self, **kwargs):
        pass

    def to_date(self, value):
        if value is None or value == '':
            return None
        return datetime.strptime(value.split('.')[0], '%Y-%d-%mT%H:%M:%S')

    def parse_pass(self, row):
        pass

    def parse_standard(self, row):
        return [
            row[4],
            row[5][-32:],
            self.to_date(row[2]),
            int(row[3]),
            row[11],
            row[10],
            RESULTS.get(row[17], 'NPI'),
            row[39],
            row[40],
            self.to_date(row[47]),
            self.to_date(row[48]),
            self.to_date(row[49]),
            self.to_date(row[50]),
            self.to_date(row[51]),
            self.to_date(row[52])
        ]

    def parse_queue(self, row):
        return [
            row[4][-32:],
            self.to_date(row[2]),
            row[6],
            self.to_date(row[7]),
            self.to_date(row[8]),
            str(ABANDON.get(int(row[10]), '0')),
            row[11]
        ]

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
                            cdr_type = CDR_TYPES[row[1]]
                            parse_method = getattr(self, cdr_type['method'], self.parse_pass)
                            line = parse_method(row)
                            report = cdr_type['report']
                            row_processor(line, report, **kwargs)
                        except Exception as e:
                            print('Can\'t parse line:', sys.exc_info()[0])
                            traceback.print_exc()