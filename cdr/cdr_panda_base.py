import os
import csv
from datetime import datetime

import pandas as pd

from .constants import STANDARD_RECORD_TYPE, FIELDS_DF

class CDRPandaBase(object):
    def __init__(self, cdr_folder=None, record_type=STANDARD_RECORD_TYPE):
        self.cdr_folder = cdr_folder or os.environ.get('CDR_FOLDER')
        self.record_type = record_type
        self.fields_df = FIELDS_DF[record_type]
        self.df = self.parse_cdr_records()

    def parse_cdr_records(self):
        print(f'Attempting to create a df from the {self.record_type} cdr records stored in {self.cdr_folder}')
        if self.record_type is None:
            print('record_type can\t be None')
            return
        if self.fields_df is None:
            print('fields_df can\t be None')
            return
        df = pd.DataFrame(self.process_cdr(), columns=self.fields_df['name'])
        self.typecast_df(df)
        self.parse_record_id(df)
        return df

    def to_date(self, d):
        if d != '':
            return datetime.strptime(d.split('-0300')[0], '%Y-%d-%mT%H:%M:%S.%f') 
        return None

    def parse_record_id(self, df):
        print(f'Attempting to parse the record_id column...')
        try:
            record_df = df['record_id'].str.split('-0300:', expand=True)
            df['record_id'] = record_df[1]
        except:
            print('Couldn\'t parse the record_id column')

    def typecast_df(self, df):
        print(f'Typecasting columns...')
        for index, row in self.fields_df.iterrows():
            if row['type'] is None or df[row['name']].dtype == 'datetime64[ns]':
                continue
            if row['type'] is 'date':
                df[row['name']] = df[row['name']].apply(self.to_date)
                continue
            df[row['name']] = df[row['name']].astype(row['type'], copy=False)

    def process_cdr(self):
        print(f'Processing cdr...')
        rows = []
        for file in os.listdir(self.cdr_folder):
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
                        if row[1] != self.record_type:
                            continue
                        rows.append([row[index - 1] for index in self.fields_df['index']])       
        return rows