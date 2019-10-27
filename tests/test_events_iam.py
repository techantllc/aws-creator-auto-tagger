# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx
import boto3
from tat_aws_creator_auto_tag.tests import iam_client
from tat_aws_creator_auto_tag.events import EventType, EventName


class TestIAMUser(object):
    create_event_record = {
        "eventVersion": "1.05",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AAAAAAAAAAAAAAAAAAAAA",
            "arn": "arn:aws:iam::111122223333:user/admin",
            "accountId": "111122223333",
            "accessKeyId": "AAAAAAAAAAAAAAAAAAAAA",
            "userName": "admin",
            "sessionContext": {
                "attributes": {
                    "mfaAuthenticated": "false",
                    "creationDate": "2019-10-26T16:29:56Z"
                }
            },
            "invokedBy": "signin.amazonaws.com"
        },
        "eventTime": "2019-10-26T22:07:04Z",
        "eventSource": "iam.amazonaws.com",
        "eventName": "CreateUser",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "111.111.111.111",
        "userAgent": "signin.amazonaws.com",
        "requestParameters": {
            "userName": "TestUserDeleteSoon",
            "tags": []
        },
        "responseElements": {
            "user": {
                "path": "/",
                "arn": "arn:aws:iam::111122223333:user/TestUser",
                "userId": "AAAAAAAAAAAAAAAAAAAAA",
                "createDate": "Oct 26, 2019 10:07:04 PM",
                "userName": "TestUser"
            }
        },
        "requestID": "aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa",
        "eventID": "aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa",
        "eventType": "AwsApiCall",
        "recipientAccountId": "111122223333"
    }

    def test_get_created_iam_user_arn(self):
        assert EventName.IAM.User.get_created_iam_user_arn(
            self.create_event_record) == "arn:aws:iam::111122223333:user/TestUser"

    def test_tag_it(self):
        EventName.IAM.User.tag_it(self.create_event_record, iam_client)


class TestIAMRole(object):
    create_event_record = {
        "eventVersion": "1.05",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AAAAAAAAAAAAAAAAAAAAA",
            "arn": "arn:aws:iam::111122223333:user/admin",
            "accountId": "111122223333",
            "accessKeyId": "AAAAAAAAAAAAAAAAAAAAA",
            "userName": "admin",
            "sessionContext": {
                "attributes": {
                    "mfaAuthenticated": "false",
                    "creationDate": "2019-10-26T16:29:56Z"
                }
            },
            "invokedBy": "signin.amazonaws.com"
        },
        "eventTime": "2019-10-26T22:19:16Z",
        "eventSource": "iam.amazonaws.com",
        "eventName": "CreateRole",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "111.111.111.111",
        "userAgent": "signin.amazonaws.com",
        "requestParameters": {
            "roleName": "TestRole",
            "description": "Allows Lambda functions to call AWS services on your behalf.",
            "assumeRolePolicyDocument": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"sts:AssumeRole\"],\"Principal\":{\"Service\":[\"lambda.amazonaws.com\"]}}]}",
            "tags": []
        },
        "responseElements": {
            "role": {
                "assumeRolePolicyDocument": "%7B%22Version%22%3A%222012-10-17%22%2C%22Statement%22%3A%5B%7B%22Effect%22%3A%22Allow%22%2C%22Action%22%3A%5B%22sts%3AAssumeRole%22%5D%2C%22Principal%22%3A%7B%22Service%22%3A%5B%22lambda.amazonaws.com%22%5D%7D%7D%5D%7D",
                "arn": "arn:aws:iam::111122223333:role/TestRole",
                "roleId": "AAAAAAAAAAAAAAAAAAAAA",
                "createDate": "Oct 26, 2019 10:19:16 PM",
                "roleName": "TestRole",
                "path": "/"
            }
        },
        "requestID": "aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa",
        "eventID": "aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa",
        "eventType": "AwsApiCall",
        "recipientAccountId": "111122223333"
    }

    def test_get_created_iam_user_arn(self):
        assert EventName.IAM.Role.get_created_iam_role_arn(
            self.create_event_record) == "arn:aws:iam::111122223333:role/TestRole"

    def test_tag_it(self):
        EventName.IAM.Role.tag_it(self.create_event_record, iam_client)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
