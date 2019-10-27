# -*- coding: utf-8 -*-

"""
**How to find out the eventName for a specific Create event**

Go to IAM policy editor: https://console.aws.amazon.com/iam/home?region=us-east-1#/policies$new?step=edit
"""

import six
import inspect
import hashlib

try:
    import typing
except:
    pass

from dateutil import parser
from troposphere_mate.canned.iam import AWSServiceName
from .logger import log


class EventType:
    aws_api_call = "AwsApiCall"
    aws_service_event = "AwsServiceEvent"
    aws_console_signin = "AwsConsoleSignin"


SERVICE_NAME_ATTR = "_service_name"
EVENT_NAME_ATTR = "_event_name"


class EventMeta(type):
    def __new__(cls, name, bases, attrs):

        _accessor_mapper = attrs["_accessor_mapper"]

        for service_name, aws_service_klass in attrs.items():
            # AwsServiceClass
            if inspect.isclass(aws_service_klass) and hasattr(aws_service_klass, SERVICE_NAME_ATTR):
                event_source_name = getattr(aws_service_klass, SERVICE_NAME_ATTR)
                _accessor_mapper.setdefault(event_source_name, dict())
                for resource_name, aws_resource_klass in aws_service_klass.__dict__.items():
                    # AwsResourceClass
                    if inspect.isclass(aws_service_klass) and hasattr(aws_resource_klass, EVENT_NAME_ATTR):
                        create_event_name = getattr(aws_resource_klass, EVENT_NAME_ATTR)
                        _accessor_mapper[event_source_name].setdefault(create_event_name, aws_resource_klass)
                        # print(_accessor_mapper)

        klass = super(EventMeta, cls).__new__(cls, name, bases, attrs)
        return klass


TAG_FIELD_PREFIX = "TechAntTag"


class TagKey:
    creator = TAG_FIELD_PREFIX + "Creator"
    creator_ip_hash = TAG_FIELD_PREFIX + "CreatorIpHash"
    create_time = TAG_FIELD_PREFIX + "CreateTime"


def list_tags_to_dict_tags(tags):
    """
    :type tags: typing.List[typing.Dict[str, str]]

    :rtype: typing.Dict[str, str]
    """
    return {
        dct["Key"]: dct["Value"]
        for dct in tags
    }


def dict_tags_to_list_tags(tags):
    """
    :type tags: typing.Dict[str, str]

    :rtype: typing.List[typing.Dict[str, str]]
    """
    return [
        {
            "Key": key, "Value": value
        }
        for key, value in tags.items()
    ]


def get_updated_tags(existing_tags, expected_tags):
    """
    :type existing_tags: typing.Dict[str, str]
    :param existing_tags: key value dict represent existing tags

    :type existing_tags: typing.Dict[str, str]
    :param expected_tags: key value dict represent expected tags

    :rtype: typing.Dict[str, str]
    """
    return {
        key: value
        for key, value in expected_tags.items() if key not in existing_tags
    }


def md5_of_text(text):
    m = hashlib.md5()
    m.update(text.encode("utf-8"))
    return m.hexdigest()


class RecordParser:
    @classmethod
    def get_creator_arn(cls, record):
        return record["userIdentity"]["arn"]

    @classmethod
    def get_creator_ip_hash(cls, record):
        return md5_of_text(record["sourceIPAddress"])

    @classmethod
    def get_create_time(cls, record):
        return str(parser.parse(record["eventTime"]))

    @classmethod
    def get_expected_tags(cls, record):
        return {
            TagKey.creator: cls.get_creator_arn(record),
            TagKey.creator_ip_hash: md5_of_text(cls.get_creator_ip_hash(record)),
            TagKey.create_time: cls.get_create_time(record),
        }

    @classmethod
    def is_create_event(cls, record):
        """
        identify whether it is a ``Create`` event.
        """
        if record["eventType"] != EventType.aws_api_call:
            return False
        if not record["eventName"].startswith("Create"):
            return False
        return True


class BaseAwsResource(object):
    @classmethod
    def tag_it(cls, record, boto_client, verbose):
        """
        :type record: dict
        :type boto_client: typing.Any
        :type verbose: bool
        """
        raise NotImplementedError


class ResourceNotSupportedError(Exception): pass


@six.add_metaclass(EventMeta)
class EventName:
    _accessor_mapper = dict()

    @classmethod
    def get_event_source_name(cls, record):
        return record["eventSource"].replace(".amazonaws.com", "")

    @classmethod
    def get_event_name(cls, record):
        return record["eventName"]

    @classmethod
    def get_resource_class(cls, event_source_name, event_name):
        """
        :type event_source_name: str
        :type event_name: str

        :rtype: BaseAwsResource
        """
        try:
            return cls._accessor_mapper[event_source_name][event_name]
        except KeyError:
            msg = "{}.{} are not supported yet!".format(event_source_name, event_name)
            raise ResourceNotSupportedError(msg)

    @classmethod
    def tag_it(cls, record, boto_ses, verbose=True):
        event_source_name = cls.get_event_source_name(record)
        event_name = cls.get_event_name(record)
        ResourceClass = cls.get_resource_class(event_source_name, event_name)
        boto_client = boto_ses.client(event_source_name)
        ResourceClass.tag_it(record, boto_client, verbose=verbose)

    class IAM:
        _service_name = AWSServiceName.aws_Identity_and_Access_Management_IAM

        class User:
            _event_name = "CreateUser"

            @classmethod
            def get_created_iam_user_arn(cls, record):
                return record["responseElements"]["user"]["arn"]

            @classmethod
            def tag_it(cls, record, iam_client, verbose=True):
                user_arn = cls.get_created_iam_user_arn(record)
                username = user_arn.split("/")[-1]

                res_list_user_tags = iam_client.list_user_tags(UserName=username)
                existing_tags = res_list_user_tags.get("Tags", list())
                existing_tags_in_dict = list_tags_to_dict_tags(existing_tags)

                expected_tags = RecordParser.get_expected_tags(record)
                updated_tags = get_updated_tags(
                    existing_tags=existing_tags_in_dict, expected_tags=expected_tags)
                if len(updated_tags):
                    res_tag_user = iam_client.tag_user(
                        UserName=username,
                        Tags=dict_tags_to_list_tags(updated_tags)
                    )
                    msg = "Successfully tagged {}.".format(user_arn)
                    log(msg, verbose=verbose)
                    return res_tag_user
                else:
                    msg = "No need to update tag for {}.".format(user_arn)
                    log(msg, verbose=verbose)
                    return {}

        class Role:
            _event_name = "CreateRole"

            @classmethod
            def get_created_iam_role_arn(cls, record):
                return record["responseElements"]["role"]["arn"]

            @classmethod
            def tag_it(cls, record, iam_client, verbose=True):
                role_arn = cls.get_created_iam_role_arn(record)
                rolename = role_arn.split("/")[-1]

                res_list_role_tags = iam_client.list_role_tags(RoleName=rolename)
                existing_tags = res_list_role_tags.get("Tags", list())
                existing_tags_in_dict = list_tags_to_dict_tags(existing_tags)

                expected_tags = RecordParser.get_expected_tags(record)
                updated_tags = get_updated_tags(
                    existing_tags=existing_tags_in_dict, expected_tags=expected_tags)
                if len(updated_tags):
                    res_tag_role = iam_client.tag_role(
                        RoleName=rolename,
                        Tags=dict_tags_to_list_tags(updated_tags)
                    )
                    msg = "Successfully tagged {}.".format(role_arn)
                    log(msg, verbose=verbose)
                    return res_tag_role
                else:
                    msg = "No need to update tag for {}.".format(role_arn)
                    log(msg, verbose=verbose)
                    return {}

    class S3:
        _service_name = AWSServiceName.amazon_Simple_Storage_Service_Amazon_S3

        class Bucket:
            _event_name = "CreateBucket"

            @classmethod
            def get_bucket_name(cls, record):
                return record["requestParameters"]["bucketName"]

            @classmethod
            def tag_it(cls, record, s3_client, verbose=True):
                bucketname = cls.get_bucket_name(record)
                try:  # tagset may not exists
                    res_get_bucket_tagging = s3_client.get_bucket_tagging(Bucket=bucketname)
                    existing_tags = res_get_bucket_tagging.get("TagSet", list())
                except:
                    existing_tags = list()
                existing_tags_in_dict = list_tags_to_dict_tags(existing_tags)

                expected_tags = RecordParser.get_expected_tags(record)
                updated_tags = get_updated_tags(
                    existing_tags=existing_tags_in_dict, expected_tags=expected_tags)
                if len(updated_tags):
                    res_put_bucket_tagging = s3_client.put_bucket_tagging(
                        Bucket=bucketname,
                        Tagging={
                            "TagSet": dict_tags_to_list_tags(updated_tags),
                        },
                    )
                    msg = "Successfully tagged arn:aws:s3:::{}.".format(bucketname)
                    log(msg, verbose=verbose)
                    return res_put_bucket_tagging
                else:
                    msg = "No need to update tag for arn:aws:s3:::{}.".format(bucketname)
                    log(msg, verbose=verbose)
                    return {}
