import json
from transformers import AutoImageProcessor, AutoModelForObjectDetection
import torch
from PIL import Image
import requests
import boto3
import urllib.parse
from io import BytesIO


s3 = boto3.client('s3')

processor = AutoImageProcessor.from_pretrained('/opt/model', local_files_only=True)
model = AutoModelForObjectDetection.from_pretrained("/opt/model", local_files_only=True, device_map="cpu")

print("Model loaded successfully")


def lambda_handler(event, context):
    """
    Lambda function that receives an image URL, processes the image, and returns model predictions.
    """

    print("Received event: ", event)
    print("Received context: ", context)

    # Extract bucket name and image key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    image_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    print(f"Bucket: {bucket_name}, Image Key: {image_key}")

    # Download the image from S3
    s3_response = s3.get_object(Bucket=bucket_name, Key=image_key)
    image_data = s3_response['Body'].read()

    image = Image.open(BytesIO(image_data))

    # Process the image
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(outputs, threshold=0.9, target_sizes=target_sizes)[
        0
    ]

    body = []
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box = [round(i, 2) for i in box.tolist()]
        body.append(
            {
                "label": model.config.id2label[label.item()],
                "score": round(score.item(), 3),
                "box": box
            }
        )
        print(
            f"Detected {model.config.id2label[label.item()]} with confidence "
            f"{round(score.item(), 3)} at location {box}"
        )

    result = {
        "predictions": body
    }

    # Save the result to the same S3 bucket, in the 'res/' folder
    result_key = image_key.replace('images/', 'res/').replace('.jpeg',
                                                              '_result.json')  # Save as JSON with a different key
    result_json = json.dumps(result)

    # Upload the result to S3
    s3.put_object(
        Bucket=bucket_name,
        Key=result_key,
        Body=result_json,
        ContentType='application/json'
    )

    print(f"Result saved to {bucket_name}/{result_key}")

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }


if __name__ == "__main__":
    print("Hello World")

    # Test the lambda function locally
    event = {
        "body": json.dumps({
            "image_url": "https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg"
        })
    }

    lambda_handler(event, None)
