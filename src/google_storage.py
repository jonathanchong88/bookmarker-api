import datetime

from google.cloud import storage
import os 

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'chatnotification-d81a8-63477ad4cbc7.json'

def cors_configuration(bucket_name):
    """Set a bucket's CORS policies configuration."""
    # bucket_name = "your-bucket-name"

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    bucket.cors = [
        {
            "origin": ["*"],
            "method": [
                "*"
            ],
            "responseHeader": [
                "*"],
            "maxAgeSeconds": 3600
        }
    ]
    bucket.patch()

    print("Set CORS policies for bucket {} is {}".format(bucket.name, bucket.cors))
    return bucket

def bucket_metadata(bucket_name):
    """Prints out a bucket's metadata."""
    # bucket_name = 'your-bucket-name'

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    print(f"ID: {bucket.id}")
    print(f"Name: {bucket.name}")
    print(f"Storage Class: {bucket.storage_class}")
    print(f"Location: {bucket.location}")
    print(f"Location Type: {bucket.location_type}")
    print(f"Cors: {bucket.cors}")
    print(f"Default Event Based Hold: {bucket.default_event_based_hold}")
    print(f"Default KMS Key Name: {bucket.default_kms_key_name}")
    print(f"Metageneration: {bucket.metageneration}")
    print(
        f"Public Access Prevention: {bucket.iam_configuration.public_access_prevention}"
    )
    print(
        f"Retention Effective Time: {bucket.retention_policy_effective_time}")
    print(f"Retention Period: {bucket.retention_period}")
    print(f"Retention Policy Locked: {bucket.retention_policy_locked}")
    print(f"Requester Pays: {bucket.requester_pays}")
    print(f"Self Link: {bucket.self_link}")
    print(f"Time Created: {bucket.time_created}")
    print(f"Versioning Enabled: {bucket.versioning_enabled}")
    print(f"Labels: {bucket.labels}")



def generate_upload_signed_url_v4(bucket, blob_name):
    """Generates a v4 signed URL for uploading a blob using HTTP PUT.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(minutes=15),
        # Allow PUT requests using this URL.
        method="PUT",
        content_type="image/jpg",
    )

    print("Generated PUT signed URL:")
    # print(url)
    # print("You can use this URL with any user agent, for example:")
    # print(
    #     "curl -X PUT -H 'Content-Type: image/jpg' "
    #     "--upload-file {}.jpeg '{}'".format(blob_name, url)
    # )
    return url


def generate_download_signed_url_v4(bucket, blob_name):
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'chatnotification-d81a8-63477ad4cbc7.json'

    # storage_client = storage.Client()
    # bucket = storage_client.bucket(bucket_name)
    # bucket.cors = [
    #     {
    #         "origin": ["*"],
    #         'method': ['PUT', 'POST'],
    #         "responseHeader": [
    #             "Access-Control-Allow-Origin"]
    #     }
    # ]
    # bucket.update()
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(minutes=15),
        # Allow GET requests using this URL.
        method="GET",
    )

    print("Generated GET signed URL:")
    # print(url)
    # print("You can use this URL with any user agent, for example:")
    # print("curl '{}'".format(url))
    return url


def delete_blob(bucket, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'chatnotification-d81a8-63477ad4cbc7.json'


    try:
        blob = bucket.blob(blob_name)
        blob.delete()

        print("Blob {} deleted.".format(blob_name))

    except:
        #return False
        print("An delete exception occurred")


def upload_blob(bucket, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    try:
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)
        blob.upload_from_file(source_file_name.stream)

        print(
            "File {} uploaded to {}.".format(
                source_file_name, destination_blob_name
            )
        )

    except:
        #return False
        print("An upload exception occurred")
    

def upload_blob_stream(bucket, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    try:
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_file(source_file_name.stream,
                              content_type=source_file_name.content_type)

        print(
            "File {} uploaded to {}.".format(
                source_file_name, destination_blob_name
            )
        )

    except:
        #return False
        print("An upload exception occurred")



    
