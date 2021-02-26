"""Generate unique job id and S3 tokens for each job."""
from random import choices
from string import ascii_lowercase, digits
from typing import List
import boto3

# TODO 2020/17/20, Elvis - Establish specific logging format to be used in
#                  Lambda functions


def create_s3_url(bucket_name: str, file_name: str, prefix_name: str) -> str:
    """Format the READ section of the APBS input file.

    :param bucket_name str: AWS S3 bucket to store file in
    :param file_name str: the filename to put under the prefix_name directory
    :param prefix_name str: the directory in the bucket_name
    :return: a URL that can be used to upload a file to the S3 bucket
    :rtype: str
    """

    object_name = f"{prefix_name}/{file_name}"
    s3_client = boto3.client("s3")

    # Generate presigned URL for file
    url = s3_client.generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket_name, "Key": object_name},
        ExpiresIn=3600,
    )
    return url


def generate_id_and_tokens(event: dict, context=None) -> dict:
    """Generate unique ID and S3 tokens for uploading files.

    :param event dict: a dictionary holding the bucket name and file list
    :param context UNKNOWN: TODO: What is this for?
    :return: a dictionary mapping filenames to S3 URLS
    :rtype: dict
    """

    # Assign object variables from Lambda event
    bucket_name: str = event["bucket_name"]
    file_list: List[str] = event["file_list"]
    job_id: str

    # Generate new job ID if not provided
    if "job_id" in event:
        job_id = event["job_id"]
    else:
        job_id = "".join(
            choices(ascii_lowercase + digits, k=10)
        )  # Random 10-character alphanumeric string

    # Create URLs with S3 tokens
    url_dict = {}
    for file_name in file_list:
        token_url = create_s3_url(bucket_name, file_name, job_id)
        url_dict[file_name] = token_url

    # Generate JSON response
    response = {
        "job_id": job_id,
        "urls": url_dict,
    }

    return response
