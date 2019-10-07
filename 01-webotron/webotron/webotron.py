#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Webotron: Deploy websites with aws

Webotor automates the process of deploying a static Website on to AWS.

"""
from pathlib import Path
import mimetypes
from functools import reduce

from botocore.exceptions import ClientError
import boto3
import click

from bucket import BucketManager

#s3 = session.resource("s3")

sesssion = None
bucket_manager = None

# Click Group to Deploy websites onto AWS
@click.group()
@click.option('--profile', default=None,
        help="Use a given AWS profile.")
def cli(profile):
    """Webtron deploying websites to AWS"""
    global session, bucket_manager

    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile
    session = boto3.Session(**session_cfg)
    bucket_manager = BucketManager(session)


# Click Command to to list all the s3 buckets present on your account.
@cli.command('list-buckets')
def list_buckets():
    """List all the s3 buckets present."""
    for buckets in bucket_manager.s3.buckets.all():
        print(buckets)


# Click Command to display objects/contents os a s3 Bucket.
@cli.command('list-bucket-objects')
# Mention arguments that we need to pass inorder to access the below method
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List the data within this buckets"""
    for objects in s3.Bucket(bucket).objects.all():
        print(objects)


# Click Comand to create or setup an existing s3 Bucket.
@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and Configure S3 bucket"""
    try:
        s3_bucket = s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={
                'LocationConstraint': session.region_name
                }
            )
    except ClientError as error:
        if error.response['Error']['Code'] == "BucketAlreadyOwnedByYou":
            s3_bucket = s3.Bucket(bucket)
        else:
            raise error

    policy = """{
        "Version":"2012-10-17",
         "Statement":[{
            "Sid":"PublicReadGetObject",
            "Effect":"Allow",
            "Principal": "*",
            "Action":["s3:GetObject"],
            "Resource":["arn:aws:s3:::%s/*"]
          }]
    } """ % s3_bucket.name

    policy = policy.strip('\n')

    pol = s3_bucket.Policy()
    pol.put(Policy=policy)

    ws = s3_bucket.Website()
    ws.put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'string'
        },
        'IndexDocument': {
            'Suffix': 'string'
        }})

def hash_data(data):
    """Generate the hash values for objects in the s3 bucket"""
    hash = md5()
    hash.update(data)

    return hash

def gen_etag(path):
    """Generate etag for the files."""
    hashes = []

    with open(path,'rb') as f:
        while True:
            data = f.read(bucket_manager.CHUNK_SIZE)

            if not data:
                break

                hashes.append(hash_data(data))

    if not hashes:
        return
    elif len(hashes) == 1:
        return "{}".format(hashes[0].hexdigest())
    else:
        hash = hash_data(reduce(lambda x,y: x + y,(h.digest() for h in hashes)))
        return '"{} - {}"'.format(hash.hexdigest(), len(hashes))



def load_mainfest(bucket):
    """Loading the Etag for the funciton."""
    paginator = bucket_manager.s3.meta.client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket= bucket.name):
        for obj in page.get('Contents', []):
            bucket_manager.manifest[obj['Key']] = obj['ETag']


# Method to upload files onto the s3 Bucket.
def upload_file(s3_bucket, path, key):
    """ A function to upload files onto the s3 Bucket."""
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'
    path = path.replace('\\', '/')
    key = key.replace("\\", "/")

    etag = gen_etag(path)
    if bucket_manager.manifest.get(key,'') == etag:
        print("Skipping an already exisitng file.")
        return

    s3_bucket.upload_file(
        path,
        key,
        ExtraArgs={
            'ContentType': content_type
        },
        Config=bucket_manager.transfer_config
        )


# Click command to sync the contents of the folder containing
# the files for the website .
@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync content of PATHNAME to BUCKET"""
    s3_bucket = bucket_manager.s3.Bucket(bucket)
    load_mainfest(s3_bucket)

    root = Path(pathname).expanduser().resolve()

    def handle_directory(target):
        for p in target.iterdir():
            if p.is_dir():
                handle_directory(p)
            if p.is_file():
                upload_file(s3_bucket, str(p), str(p.relative_to(root)))

    handle_directory(root)
    print(bucket_manager.get_bucket_url(s3_bucket))


if __name__ == "__main__":
    cli()
