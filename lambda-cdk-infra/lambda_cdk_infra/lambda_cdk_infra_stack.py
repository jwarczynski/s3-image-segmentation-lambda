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

        ecr_repository = Repository.from_repository_name(
            self, "ECRRepository",
            repository_name="mlops/vision"
        )

        api_image_code = DockerImageCode.from_ecr(
            repository=ecr_repository,
            # cmd=["src/lambda_function.lambda_handler"]
        )

        bucket_name = "image-segmentation-bucket"
        bucket = self.get_or_create_bucket(bucket_name)

        # Reference the existing role
        lambda_role = iam.Role.from_role_arn(
            self, "LambdaS3TriggerRole",
            role_arn=f"arn:aws:iam::{os.getenv("AWS_ACCOUNT_ID")}:role/lambda-s3-trigger-role"
        )

        # Create an inline policy that allows S3 GetObject access
        s3_access_policy = iam.Policy(self, "S3AccessPolicy",
                                      statements=[
                                          iam.PolicyStatement(
                                              actions=["s3:GetObject"],
                                              resources=[f"arn:aws:s3:::{bucket_name}/images/*"]
                                              # Grant GetObject only on the images/ folder
                                          ),
                                          iam.PolicyStatement(
                                              actions=["s3:PutObject"],
                                              resources=[f"arn:aws:s3:::{bucket_name}/res/*"]
                                              # Grant PutObject only on the res/ folder
                                          )
                                      ]
                                      )

        # Attach the inline policy to the Lambda role
        s3_access_policy.attach_to_role(lambda_role)

        # Trigger the Lambda function on .jpeg file uploads in the images/ folder
        s3_event_source = eventsources.S3EventSource(
            bucket,
            events=[s3.EventType.OBJECT_CREATED],  # Trigger on object creation
            filters=[s3.NotificationKeyFilter(prefix="images/", suffix=".jpeg")]  # Only .jpeg in images/ folder
        )

        # api_image_code = DockerImageCode.from_image_asset(
        #     directory="../image",
        #     file="Dockerfile",
        #     # cmd=["lambda_function.lambda_handler"]
        # )

        api_function = DockerImageFunction(
            self, "ImageSegmentationOnS3Upload",
            function_name="ImageSegmentationOnS3Upload",
            code=api_image_code,
            timeout=Duration.seconds(15),
            memory_size=1024,
            environment={
                "ENVIRONMENT": "production",
            },
            events=[s3_event_source],
            role=lambda_role,
            retry_attempts=0,
            max_event_age=Duration.minutes(1),
        )

        function_url = api_function.add_function_url(
            auth_type=FunctionUrlAuthType.NONE
        )

        CfnOutput(self, "FunctionUrl", value=function_url.url)
        CfnOutput(self, "BucketName", value=bucket.bucket_name)

    def get_or_create_bucket(self, bucket_name) -> s3.Bucket:
        # try:
        # Step 1: Try to reference an existing bucket by name
        return self.create_bucket(bucket_name)
        bucket = s3.Bucket.from_bucket_name(
            self, bucket_name,
            bucket_name=bucket_name
        )
        print(f"Using existing bucket: {bucket_name}")
        return bucket
        # except ClientError as e:
        #     # This catches client errors (e.g., permissions issues, misconfigurations)
        #     print(f"ClientError: {e}")
        # except Exception as e:
        #     # Catches any other unexpected errors
        #     print(f"An unexpected error occurred: {e}")
        #     # Step 2: If the bucket doesn't exist or another error occurs, create a new one
        #     print(f"Bucket '{bucket_name}' not found. Creating a new bucket.")
        # bucket = self.create_bucket(bucket_name)
        #
        # return bucket

    def create_bucket(self, bucket_name) -> s3.Bucket:
        bucket: s3.Bucket = s3.Bucket(
            self, bucket_name,
            bucket_name=bucket_name,
            removal_policy=RemovalPolicy.DESTROY,  # Optional: destroy bucket if stack is deleted
            auto_delete_objects=True,  # Optional: auto-delete objects on bucket removal
        )
        return bucket