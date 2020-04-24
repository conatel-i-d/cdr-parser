import sys
import shutil

from dotenv import load_dotenv
from cdr import cdr

load_dotenv()

if __name__ == '__main__':
    cdr().my_download_latests_cdr(object_prefix='')
