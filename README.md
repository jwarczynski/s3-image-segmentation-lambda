# S3 Image Segmentation Lambda

This project performs image segmentation on images uploaded to an AWS S3 bucket. When an image is uploaded to the `images/` folder, it triggers an AWS Lambda function (built from a Docker image). The Lambda function processes the image, performs segmentation, and stores the results in the `res/` folder of the same bucket as a JSON file. The entire infrastructure is provisioned using AWS CDK.

## Features

- **Image Segmentation**: Automatic segmentation of images uploaded to S3.
- **AWS Lambda**: Triggered by S3 upload, runs a model for image segmentation.
- **Dockerized Lambda**: The Lambda function is packaged as a Docker image.
- **AWS CDK**: Infrastructure as code to deploy the S3 bucket, Lambda function, and necessary IAM permissions.
- **JSON Output**: Segmentation results are stored in the S3 bucket as JSON.

## Project Architecture

1. An image is uploaded to the `images/` folder in the S3 bucket.
2. S3 triggers a Lambda function.
3. The Lambda function:
   - Downloads the image from the bucket.
   - Processes the image using the segmentation model.
   - Uploads the result to the `res/` folder in JSON format.
4. All infrastructure (S3 bucket, Lambda function, and permissions) is created using AWS CDK.

## Requirements

- AWS CLI configured with appropriate credentials.
- AWS CDK installed.
- Docker installed for building the Lambda image.
- Python 3.x.

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/s3-image-segmentation-lambda.git
   cd s3-image-segmentation-lambda/lambda-cdk-infra
   python -m pip install -r requirements.txt
   aws configure
    ```
2. **Build the Lambda Docker image**:
   ```bash
   cd ../image
   docker build -t s3-image-segmentation-lambda .
   ```

3. **Set environment variables**:

   a) In PowerShell
   ```Powershell
    $env:AWS_ACCOUNT_ID="<account-id>"
    $env:REGION="<region>"
    ```
    
   b) In bash
    ```bash
    export AWS_ACCOUNT_ID="<account-id>"
    export REGION="<region>"
    ```
4. **Push the Docker image to ECR**:

    a) In PowerShell
    ```Powershell
    aws ecr get-login-password --$env:REGION | docker login --username AWS --password-stdin "$env:AWS_ACCOUNT_ID.dkr.ecr.$env:REGION.amazonaws.com"
    docker tag s3-image-segmentation-lambda:latest "$env:AWS_ACCOUNT_ID.dkr.ecr.$env:REGION.amazonaws.com/s3-image-segmentation-lambda:latest"
    docker push "$env:AWS_ACCOUNT_ID.dkr.ecr.$env:REGION.amazonaws.com/s3-image-segmentation-lambda:latest"
    ```
   b) In bash
   ```bash
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
    docker tag s3-image-segmentation-lambda:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/s3-image-segmentation-lambda:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/s3-image-segmentation-lambda:latest
    ```
   
5. **Deploy the infrastructure**:
    ```bash
    cd ../lambda-cdk-infra
    cdk deploy
    ```
    
    
   
   
