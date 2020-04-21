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
            return ''
        return datetime.strptime(value.split('.')[0], '%Y-%d-%mT%H:%M:%S')

    def parse_pass(self, row):
        pass

    def to_minutes_date_diff(self, start, end):
        if start is '' or end is '':
            return ''
        return round((end - start).total_seconds() / 60, 2)

    def check_if_is_agent_call(self, origin, destination):
        return ("598" + destination) == origin

    def check_if_is_abandoned_call(self, origin, destination, duration):
        return destination == "59879710100" and origin != "59839030106" and duration == 0

    def parse_standard(self, row):
        time = self.to_date(row[2])
        pickup_time = self.to_date(row[47])
        hang_time = self.to_date(row[48])
        duration = int(row[3])
        origin = row[11]
        destination = row[10]
        return [
            row[4],
            row[5][-32:],
            time,
            duration,
            origin,
            destination,
            RESULTS.get(int(row[17]), 'NPI'),
            row[39],
            row[40],
            pickup_time,
            hang_time,
            self.to_date(row[49]),
            self.to_date(row[50]),
            self.to_date(row[51]),
            self.to_date(row[52]),
            self.to_minutes_date_diff(time, pickup_time), # wait_time
            self.to_minutes_date_diff(time, hang_time),   # session_time
            round(duration / 10 / 60, 2),                 # duration_minutes
            self.check_if_is_agent_call(origin, destination),
            self.check_if_is_abandoned_call(origin, destination, duration)
        ]

    def parse_queue(self, row):
        time = self.to_date(row[2])
        start_time = self.to_date(row[7])
        end_time = self.to_date(row[8])
        return [
            row[4][-32:],
            time,
            row[6],
            start_time,
            end_time,
            str(ABANDON.get(int(row[10]), '0')),
            row[11],
            self.to_minutes_date_diff(start_time, end_time)
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