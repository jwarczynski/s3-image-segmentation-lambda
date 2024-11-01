import aws_cdk as core
import aws_cdk.assertions as assertions

from lambda_cdk_infra.lambda_cdk_infra_stack import LambdaCdkInfraStack

# example tests. To run these tests, uncomment this file along with the example
# resource in lambda_cdk_infra/lambda_cdk_infra_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = LambdaCdkInfraStack(app, "lambda-cdk-infra")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
