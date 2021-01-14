import boto3
from flask import make_response
import json, os, uuid
from app import make_json_response
from query import get_manifest_data, get_metadata
from manifest_handler import ManifestHandler

class AwsHandler(ManifestHandler):
    """
    Sends manifest/metadata file to Amazon Web Services (AWS) S3 bucket, and
    returns a unique string that is required for the user to access the file on
    the bucket.

    """

    def __init__(self, aws_api_key=None, aws_secret_key=None, aws_bucket_name=None, aws_running_on_ec2=None, **kwargs):
        # initialize baseClass first
        super(AwsHandler, self).__init__(**kwargs)

        # now populate subClass properties
        self.aws_api_key = aws_api_key
        self.aws_secret_key = aws_secret_key
        self.aws_bucket_name = aws_bucket_name
        self.aws_running_on_ec2 = aws_running_on_ec2

        if aws_api_key is None and aws_secret_key is None and \
        aws_bucket_name is None and aws_running_on_ec2 is None:
            # Build filepath to config file
            dir_path = os.path.dirname(os.path.realpath(__file__))
            config_filepath = os.path.join(dir_path, 'config.ini')

            # Get AWS config
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.read(config_filepath)
            self.aws_api_key = config.get('cloud-options', 'aws-api-key')
            self.aws_secret_key = config.get('cloud-options', 'aws-secret-key')
            self.aws_bucket_name = config.get('cloud-options', 'aws-bucket-name')
            self.aws_running_on_ec2 = json.loads(config.get('cloud-options', 'aws-running-on-ec2').lower())

        else:
            raise("Error: AWS arguments must be provided via config.ini")


    def handle_manifest(self, request):
        """
        Send manifest_id file to S3 bucket
        Returns JSON containing 'manifest_id' if successfully uploaded to bucket,
            if error, returns JSON containing 'error'
        """
        string = ""

        ids = json.loads(request.data)['ids']
        data = get_manifest_data(ids) # get all the relevant properties for this file

        for result in data:
            string += result

        response_obj = self._upload_file(file_contents=string)

        response_str = json.dumps(response_obj)
        response = make_response(response_str)
        return make_json_response(response) #Stringified {'manifest_id': 'xxx-xxxxxxx-xxxx-xxxxx'}

    def handle_metadata(self, request):
        """
        Send metadata file to S3 bucket
        Returns JSON containing 'manifest_id' if successfully uploaded to bucket,
            if error, returns JSON containing 'error'
        """
        ids = json.dumps(json.loads(request.data)['ids'])
        data = get_metadata(ids)

        response_obj = self._upload_file(file_contents=data)

        response_str = json.dumps(response_obj)
        response = make_response(response_str)
        return make_json_response(response) #Stringified {'manifest_id': 'xxx-xxxxxxx-xxxx-xxxxx'}

    def _upload_file(self, file_contents):
        """
        Accesses AWS client and uploads file data.
        On upload success, seturns UID so user can later access the file.
        On upload error, returns error message. 
        """
        #Generate UID for naming file in bucket
        uid = str(uuid.uuid4())
        file_name = self.file_name + '_' + uid + '.tsv'

        session = boto3.Session()
        s3_client = None

        if not self.aws_running_on_ec2:
            s3_client = boto3.client(
                's3',
                aws_access_key_id = self.aws_api_key,
                aws_secret_access_key = self.aws_secret_key
            )
        else:
            credentials = session.get_credentials()

            # Credentials are refreshable, so accessing your access key / secret key
            # separately can lead to a race condition. Use this to get an actual matched
            # set.
            credentials = credentials.get_frozen_credentials()

            # Get the service client
            s3_client = boto3.client(
                's3',
                aws_access_key_id = credentials.access_key,
                aws_secret_access_key = credentials.secret_key,
                aws_session_token = credentials.token
            )

        try:
            response = s3_client.put_object(
        	Bucket = self.aws_bucket_name,
        	Body = file_contents,
        	Key = file_name,
        	ServerSideEncryption = 'AES256'
            )
            return {'manifest_id': uid}
        except:
            return {'error': 'Unable to upload file to AWS bucket.'}
