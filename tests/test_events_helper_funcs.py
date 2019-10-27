# -*- coding: utf-8 -*-

import pytest
from tat_aws_creator_auto_tag import events


def test_list_tags_to_dict_tags():
    assert events.list_tags_to_dict_tags([{"Key": "Name", "Value": "Alice"}]) == {"Name": "Alice"}


def test_dict_tags_to_list_tags():
    assert events.dict_tags_to_list_tags({"Name": "Alice"}) == [{"Key": "Name", "Value": "Alice"}]


def test_md5_of_text():
    assert events.md5_of_text("192.168.0.1") == "f0fdb4c3f58e3e3f8e77162d893d3055"


class TestRecordParser(object):
    create_iam_user_event_record = {
        "eventVersion": "1.05",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "ABCD",
            "arn": "arn:aws:iam::111122223333:user/admin",
            "accountId": "111122223333",
            "accessKeyId": "ABCD",
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
                "userId": "ABCD",
                "createDate": "Oct 26, 2019 10:07:04 PM",
                "userName": "TestUser"
            }
        },
        "requestID": "aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa",
        "eventID": "aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa",
        "eventType": "AwsApiCall",
        "recipientAccountId": "111122223333"
    }

    def test_get_username(self):
        assert events.RecordParser.get_creator_arn(self.create_iam_user_event_record) \
               == "arn:aws:iam::111122223333:user/admin"

    def test_get_creator_ip_hash(self):
        assert "." not in events.RecordParser.get_creator_ip_hash(self.create_iam_user_event_record)

    def test_get_create_time(self):
        assert events.RecordParser.get_create_time(self.create_iam_user_event_record) \
               == "2019-10-26 22:07:04+00:00"


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
