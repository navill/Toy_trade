from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    location = 'media'
    bucket_name = 's3django-upload'
    AWS_REGION = 'ap-northeast-2'
    AWS_STORAGE_BUCKET_NAME = 's3django-upload'
    custom_domain = '%s.s3.%s.amazonaws.com' % (AWS_STORAGE_BUCKET_NAME, AWS_REGION)
    file_overwrite = False
