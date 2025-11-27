import oss2
import os
from itertools import islice

# 从环境变量中获取访问凭证

# 设置Endpoint和Region


bucket = None
def get_oss_bucket():
    global bucket
    if bucket:
        return bucket
   
    endpoint = os.getenv("ALIYUN_OSS_ENDPOINT")
    bucket_name = os.getenv("ALIYUN_OSS_BUCKET")
    region = os.getenv("ALIYUN_OSS_REGION")
    ALIYUN_ACCESS_KEY_ID = os.getenv("ALIYUN_ACCESS_KEY_ID")
    ALIYUN_ACCESS_KEY_SECRET = os.getenv("ALIYUN_ACCESS_KEY_SECRET")

    if endpoint and bucket_name and region and ALIYUN_ACCESS_KEY_ID and ALIYUN_ACCESS_KEY_SECRET:
        auth = oss2.Auth(ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        # print("Connected to OSS bucket:", bucket_name)
    return bucket


def list_objects():
    try:
        bucket = get_oss_bucket()
        objects = list(islice(oss2.ObjectIterator(bucket), 10))
        pass
        # for obj in objects:

    except oss2.exceptions.OssError as e:
        e.with_traceback()
        

