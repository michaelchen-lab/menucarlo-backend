from storages.backends.s3boto3 import S3Boto3Storage

class UserDataStorage(S3Boto3Storage):
    location = 'user_data'
