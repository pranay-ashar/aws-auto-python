# -*- coding: utf-8 -*-

""" Classes for s3 Bucekts. """

import util
import boto3

class BucketManager:
    """Manage an s3 Bucket"""

    CHUNK_SIZE = 8388608

    def __init__(self, session):
        """Create a bucekt Manager Object."""
        self.s3 = session.resource('s3')
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_chunksize=self.CHUNK_SIZE,
            multipart_threshold=self.CHUNK_SIZE
        )
        self.manifest = {}

    def get_region_name(self,bucket):
        """Get the buckets region name."""
        bucket_location = self.s3.meta.client.get_bucket_location(Bucket = bucket.name)
        return bucket_location['LocationConstraint'] or 'us-east-1'

    def get_bucket_url(self,bucket):
        """To get the URL for the given bucket."""
        return "http://{}.{}".format(bucket.name,
            util.get_endpoint(self.get_region_name(bucket)).host)
