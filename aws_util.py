import boto3
import botocore
import ConfigParser
import os

# Build filepath to config file
dir_path = os.path.dirname(os.path.realpath(__file__))
config_filepath = os.path.join(dir_path, 'config.ini')

# Load config.ini
config = ConfigParser.ConfigParser()
config.read(config_filepath)
cloudConfig = {
    'running_on_ec2': config.get('cloud-options', 'aws-running-on-ec2'),
    'api_key': config.get('cloud-options', 'aws-api-key'),
    'secret_key': config.get('cloud-options', 'aws-secret-key'),
    'bucket_name': config.get('cloud-options','aws-bucket-name')
}

def download_manifest(filename):
    """
    Used by API route function retrieve_manifest() in ./app.py.

    """

    s3_resource = None
    session = boto3.Session()

    if not cloudConfig['running_on_ec2']:
        s3_resource = boto3.resource(
            's3',
            aws_access_key_id=cloudConfig['api_key'],
            aws_secret_access_key=cloudConfig['secret_key']
        )
    else:
        credentials = session.get_credentials()

        # Credentials are refreshable, so accessing your access key / secret key
        # separately can lead to a race condition. Use this to get an actual matched
        # set.
        credentials = credentials.get_frozen_credentials()
        s3_resource = boto3.resource(
            's3',
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            aws_session_token=credentials.token
        )

    try:
        # the .load() function does a quick head-type call on the object to test for
        # existence. Use this to find out if the object exists so we don't error out
        # trying to access the object's 'Body' and instead thrown an exception
        # s3_resource.Object(bucket_name, filename).load()
        # manifest_obj = s3_resource.Object(bucket_name, filename)
        s3_resource.Object(cloudConfig['bucket_name'], filename).load()
        manifest_obj = s3_resource.Object(cloudConfig['bucket_name'], filename)
        return manifest_obj.get()['Body'].read().decode('utf-8')
    except botocore.exceptions.ClientError as e:
        # Could check here if the error code is a 404 (which would be the case if the
        # ID passed in is invalid. However, just going to raise an error and handle them
        # all the same at this time:
        #if e.response['Error']['Code'] == "404":
        #    return "The object does not exist."
        raise
