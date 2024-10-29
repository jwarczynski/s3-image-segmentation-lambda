import os

from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    aws_s3 as s3,
    aws_lambda_event_sources as eventsources,
    RemovalPolicy,
    aws_iam as iam
)
from constructs import Construct
from aws_cdk.aws_lambda import DockerImageCode, DockerImageFunction, FunctionUrlAuthType
from aws_cdk.aws_ecr import Repository
from botocore.exceptions import ClientError


class LambdaCdkInfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get reference to the ECR with the lambda function image
        ecr_repository = Repository.from_repository_name(
            self, "ECRRepository",
            repository_name="s3-image-segmentation-lambda"
        )

        # Get image with lambda function form ECR
        api_image_code = DockerImageCode.from_ecr(
            repository=ecr_repository,
        )

        # Create new role for Lambda function
        lambda_role = iam.Role(self, "LambdaS3TriggerRole2",
                               assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[
                                   iam.ManagedPolicy.from_aws_managed_policy_name(
                                       "service-role/AWSLambdaBasicExecutionRole"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name(
                                       "service-role/AWSLambdaVPCAccessExecutionRole"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaRole")
                               ]
                               )

        api_function = DockerImageFunction(
            self, "ImageSegmentationOnS3Upload",
            function_name="ImageSegmentationOnS3Upload",
            code=api_image_code,
            timeout=Duration.seconds(30),
            memory_size=2048,
            environment={
                "ENVIRONMENT": "production",
            },
            role=lambda_role,
            retry_attempts=0,
            max_event_age=Duration.minutes(1),
        )

    def create_bucket(self, bucket_name) -> s3.Bucket:
        bucket: s3.Bucket = s3.Bucket(
            self, bucket_name,
            bucket_name=bucket_name,
            removal_policy=RemovalPolicy.DESTROY,  # Optional: destroy bucket if stack is deleted
            auto_delete_objects=True,  # Optional: auto-delete objects on bucket removal
        )
        return bucket
