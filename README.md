# AWS Automation using Python.

Repository for to develop projects to create apps for AWS automation using Python.

## 01 - Webotron :-

Webotron is a script that will sync a local directory to an s3bucket, and optionally configure Route 53 and cloudfront as well.

### Features

Webotron currently has the following Features:

- Method list_buckets to list all the s3 Buckets peresnt in the account.
- Method list_bucket_objects to list all the objects within a specific s3 bucket.
- Method setup_bucket to create and setup a new bucket with necessary policies.
- Method handle_directory to sync directory tree to a bucket.
