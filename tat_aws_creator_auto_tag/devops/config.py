# -*- coding: utf-8 -*-

from pathlib_mate import Path
from configirl import ConfigClass, Constant, Derivable


class Config(ConfigClass):
    CONFIG_DIR = Path(__file__).parent.parent.parent.append_parts("config").abspath

    METADATA = Constant(default=dict())

    PROJECT_NAME = Constant()
    PROJECT_NAME_SLUG = Derivable()

    @PROJECT_NAME_SLUG.getter
    def get_project_name_slug(self):
        return self.PROJECT_NAME.get_value().replace("_", "-")

    STAGE = Constant()  # example dev / test / prod

    ENVIRONMENT_NAME = Derivable()

    @ENVIRONMENT_NAME.getter
    def get_ENVIRONMENT_NAME(self):
        return "{}-{}".format(self.PROJECT_NAME_SLUG.get_value(self), self.STAGE.get_value())

    AWS_ACCOUNT_ID = Constant()
    AWS_REGION = Constant()
    AWS_PROFILE_FOR_DEPLOY = Constant()

    AWS_PROFILE_FOR_BOTO3 = Derivable()

    @AWS_PROFILE_FOR_BOTO3.getter
    def get_AWS_PROFILE_FOR_BOTO3(self):
        if self.is_aws_lambda_runtime():
            return None
        else:
            return self.AWS_PROFILE_FOR_DEPLOY.get_value()

    S3_BUCKET_FOR_DEPLOY = Constant()

    S3_BUCKET_FOR_CLOUDTRAIL = Constant()

    LAMBDA_ENV_VAR_PREFIX = Constant(default="TAT_AWS_CREATOR_AUTO_TAG_")

    IAM_ROLE_NAME = Constant()

    IAM_ROLE_ARN = Derivable()

    @IAM_ROLE_ARN.getter
    def get_IAM_ROLE_ARN(self):
        return "arn:aws:iam::{}:role/{}".format(
            self.AWS_ACCOUNT_ID.get_value(),
            self.IAM_ROLE_NAME.get_value(),
        )

    LATEST_LAYER_ARN = Derivable()

    @LATEST_LAYER_ARN.getter
    def get_LATEST_LAYER_ARN(self):
        """
        """
        import boto3

        boto_ses = boto3.Session(profile_name=self.AWS_PROFILE_FOR_BOTO3.get_value())
        lbd_client = boto_ses.client("lambda")
        res_list_layers = lbd_client.list_layers(
            CompatibleRuntime="python3.6"
        )
        latest_layer_arn = None
        for layer_data in res_list_layers["Layers"]:
            layer_name = layer_data["LayerName"]
            if layer_name == self.PROJECT_NAME.get_value():
                latest_layer_arn = layer_data["LatestMatchingVersion"]["LayerVersionArn"]
        if latest_layer_arn is None:
            raise ValueError
        return latest_layer_arn
