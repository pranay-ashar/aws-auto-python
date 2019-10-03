import boto3
import click

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

if __name__ == "__main__":
    cli()
