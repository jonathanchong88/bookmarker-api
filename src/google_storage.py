import datetime

from google.cloud import storage
import os 




def generate_upload_signed_url_v4(bucket_name, blob_name):
    """Generates a v4 signed URL for uploading a blob using HTTP PUT.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'chatnotification-d81a8-63477ad4cbc7.json'
    storage_client = storage.Client()

    # print(dir(storage_client))
    # url = 'hello testing'
    bucket = storage_client.bucket(bucket_name)
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
    print(url)
    print("You can use this URL with any user agent, for example:")
    print(
        "curl -X PUT -H 'Content-Type: image/jpg' "
        "--upload-file {}.jpeg '{}'".format(blob_name, url)
    )
    return url


def generate_download_signed_url_v4(bucket_name, blob_name):
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'chatnotification-d81a8-63477ad4cbc7.json'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(minutes=15),
        # Allow GET requests using this URL.
        method="GET",
    )

    print("Generated GET signed URL:")
    print(url)
    print("You can use this URL with any user agent, for example:")
    print("curl '{}'".format(url))
    return url


def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'chatnotification-d81a8-63477ad4cbc7.json'


    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()

        print("Blob {} deleted.".format(blob_name))

    except:
        #return False
        print("An exception occurred")
    


    
