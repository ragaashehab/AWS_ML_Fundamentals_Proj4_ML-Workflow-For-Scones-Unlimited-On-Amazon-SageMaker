#Lambda function_1 "serialize" will copy an object from S3, base64 encode it, and then return it to the step function as image_data in an event.
"""
            "image_data": "",
            "s3_bucket": "sagemaker-us-east-1-041508320717",
            "s3_key": "test/bicycle_s_000513.png",
            "inferences": []
"""
import json
import boto3
import botocore
import base64

s3 = boto3.resource('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key'] ## TODO: fill in
    bucket = event['s3_bucket'] ## TODO: fill in
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in : https://boto3.amazonaws.com/v1/documentation/api/1.9.42/guide/s3-example-download-file.html
    try:
        s3.Bucket(bucket).download_file(key, '/tmp/image.png')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    #print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

##########################################################################################
# Lambda function_2 "classify" is responsible for the classification part 
#- we're going to take the image output from the previous function, decode it, and then pass inferences back to the the Step Function.

import json
import base64
import boto3

#import sagemaker
#from sagemaker.predictor import Predictor
#from sagemaker.serializers import IdentitySerializer


# Fill this in with the name of your deployed model
## https://aws.amazon.com/blogs/machine-learning/call-an-amazon-sagemaker-model-endpoint-using-amazon-api-gateway-and-aws-lambda/
ENDPOINT = 'image-classification-2023-09-05-09-46-25-714'  ## TODO: fill in os.environ['image-classification-2023-07-20-09-21-14-720'] 
runtime= boto3.client('runtime.sagemaker')  


def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']['image_data']) ## TODO: fill in

    # https://sagemaker.readthedocs.io/en/v2.30.0/api/inference/serializers.html
    #https://sagemaker-examples.readthedocs.io/en/latest/sagemaker_model_monitor/introduction/SageMaker-ModelMonitoring.html
    # Instantiate a Predictor
    # For this model the IdentitySerializer needs to be "image/png"
    #predictor = Predictor(endpoint_name=ENDPOINT, serializer= IdentitySerializer("image/png")
    #predictor.serializer = IdentitySerializer("image/png")

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime/client/invoke_endpoint.html
    predictor = runtime.invoke_endpoint(EndpointName=ENDPOINT, ContentType='application/x-image', Body=image)  ## TODO: fill in

    
    # Make a prediction:
    inferences = predictor['Body'].read().decode('utf-8')  ## TODO: fill in 
    #event["inferences"] = predictor['Body'].read().decode('utf-8')  ## TODO: fill in 
    
    # We return the data back to the Step Function  
    #event["inferences"] = [float(x) for x in inferences[1:-1].split(',')] 
    return {
        'statusCode': 200,
        'body': {
            "image_data": event['body']['image_data'],
            "s3_bucket": event['body']['s3_bucket'],
            "s3_key": event['body']['s3_key'],
            "inferences": inferences
        }
    }

##################################################################################3
#lambda function_3 "filter" low-confidence inferences according to threashold bet 0.0 and 1.0. 
# pass that inference along to downstream systems

import json


THRESHOLD = .7


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = event['body']["inferences"]  ## TODO: fill in    

    # Check if any values in our inferences are above THRESHOLD
    ## TODO: fill in         meets_threshold =   ## TODO: fill in
    meets_threshold = any(x >= THRESHOLD for x in inferences)

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': {         #   'body': json.dumps(event)
           "image_data": event['body']['image_data'],
            "s3_bucket": event['body']['s3_bucket'],
            "s3_key": event['body']['s3_key'],
            "inferences": event['body']['inferences']
        }
         
    }
"""
  
"""