import os
import json

import boto3
from dotenv import load_dotenv

boto3.set_stream_logger(name='botocore')

load_dotenv()

s3 = boto3.resource('s3')

def get_last_modified(obj):
    return obj.last_modified

def download_latests_cdr():
    prefix = os.environ.get('PREFIX')
    bucket = s3.Bucket(os.environ.get('BUCKET'))
    cdr_objects = bucket.objects.filter(Prefix=os.environ.get('PREFIX'), MaxKeys=1000)
    sorted_cdr_objects = sorted(cdr_objects, key=get_last_modified, reverse=True)
    for cdr_object in sorted_cdr_objects[0:10]:
        print(cdr_object.key)

if __name__ == '__main__':
    download_latests_cdr()