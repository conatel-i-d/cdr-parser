import sys

from dotenv import load_dotenv
from cdr import cdr

load_dotenv()

if __name__ == '__main__':
    cdr().download_latests_cdr(sys.argv[1])