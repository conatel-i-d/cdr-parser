import sys

from dotenv import load_dotenv
from cdr import cdr

load_dotenv()

if __name__ == '__main__':
    cdr().split_csv_report(sys.argv[1])