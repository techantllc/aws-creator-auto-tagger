import boto3
import json
import gzip

aws_profile = "tat_sanhe"

boto_ses = boto3.Session(profile_name=aws_profile)
s3_client = boto_ses.client("s3")

bucket_name = "tech-ant-api-call-log"
res_list_objects = s3_client.list_objects(
    Bucket=bucket_name,
    Prefix="AWSLogs/698408381665/CloudTrail/us-east-1/2019/10/27/",
)

for dct in res_list_objects["Contents"]:
    s3_key = dct["Key"]
    res_get_object = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    content = res_get_object["Body"].read()
    json_str = gzip.decompress(content).decode("utf-8")
    if "TestUserSanhe" in json_str:
        print("{} - CreateUser".format(s3_key))
    if "TestRoleSanhe" in json_str:
        print("{} - CreateRole".format(s3_key))
    if "tech-ant-test-bucket-sanhe" in json_str:
        print("{} - CreateBucket".format(s3_key))
