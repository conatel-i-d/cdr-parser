import os

from dotenv import load_dotenv
from cdr import CDRPanda

load_dotenv()

if __name__ == '__main__':
    CDRPanda().queue_calls_behaviour(
        queue_number=os.environ.get('QUEUE_NUMBER'),
        pre_attendant_number=os.environ.get('PRE_ATTENDANT_NUMBER'),
        originating_number_regex=os.environ.get('ORIGINATING_NUMBER_REGEX'),
        calls_summary_file_path=os.environ.get('CALLS_SUMMARY_FILE_PATH'),
        freq='6h'
    )