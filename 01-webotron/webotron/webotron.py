import boto3
import click
from botocore.exceptions import ClientError

session = boto3.Session(profile_name = "pythonAutomation")
s3 = session.resource("s3")

@click.group()
def cli():
    "Webtron deploying websites to AWS"
    pass

@cli.command('list-buckets')
def list_buckets():
    "List all the s3 buckets present."
    for buckets in s3.buckets.all():
        print(buckets)

@cli.command('list-bucket-objects')
@click.argument('bucket')    # To mention the arguments that we need to pass inorder to access the below method.
def list_bucket_objects(bucket):
    "List the data within this buckets"
    for objects in s3.Bucket(bucket).objects.all():
        print(objects)

@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    "Create and Configure S3 bucket"
    try:
        s3_bucket = s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration = {'LocationConstraint':session.region_name}
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "BucketAlreadyOwnedByYou":
            s3_bucket = s3.Bucket(bucket)
        else:
            raise e


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
    print(policy)

    pol = s3_bucket.Policy()
    pol.put(Policy=policy)

    ws = s3_bucket.Website()
    ws.put(WebsiteConfiguration = {
        'ErrorDocument': {
            'Key': 'string'
        },
        'IndexDocument': {
            'Suffix': 'string'
        }})

    return

if __name__ == "__main__":
    cli()
