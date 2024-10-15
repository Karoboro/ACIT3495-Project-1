from dotenv import load_dotenv
import os
import boto3

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")


def empty_bucket():
    s3 = boto3.resource(service_name='s3',
                        region_name='us-west-2',
                        aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_SECRET_KEY)
    bucket = s3.Bucket(S3_BUCKET)
    bucket.objects.all().delete()


if __name__ == "__main__":
    empty_bucket()
