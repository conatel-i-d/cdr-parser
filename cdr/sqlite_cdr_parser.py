import os

import sqlite3

from cdr.cdr_parser import CDRParser
from cdr.constants import STANDARD_FIELDS, QUEUE_FIELDS

class SqliteCDRParser(CDRParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_path = kwargs.get('db_path', './db.sql')
        self.sqlite_conn = sqlite3.connect(self.db_path, isolation_level=None)
    
    def delete_database(self):
        print('Deleting database...')
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        else:
            print(f'Database file {self.db_path} not found. Continuing...')

    def create_database(self):
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

    def parse(self, **kwargs):
        if kwargs.get('clean', False) is True:
            self.delete_database()
            self.create_database()
        self.cursor = self.sqlite_conn.cursor()
        self.process_files(self.write_line_to_sqlite)

    def write_line_to_sqlite(self, line, report):
        if report is None:
            return
        if report is 'standard':
            self.insert_line_in_standard_table(line)
        if report is 'queue':
            self.insert_line_in_queue_table(line)

    def insert_line_in_standard_table(self, line):
        sql = f"""
            INSERT INTO standard (
                {", ".join(STANDARD_FIELDS)}
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        self.cursor.execute(sql, line)

    def insert_line_in_queue_table(self, line):
        sql = f"""
            INSERT INTO queue (
                {", ".join(QUEUE_FIELDS)}
            ) VALUES (?,?,?,?,?,?,?)
        """
        self.cursor.execute(sql, line)