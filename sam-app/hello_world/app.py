import googlemaps
from datetime import datetime
import json
import time
import os
import boto3
import requests
import csv

class Controller():

    def __init__(self, local):
        if local:
            self.key = key=os.environ['gkey']
        else:
            # can pull from aws secrets
            self.key = "REPLACEME"

    def get_places(self, place):
        # area within 500 m of centennial park for keywords
        radius = 1000
        total = []
        gmaps = googlemaps.Client(key=self.key)
        # from NSW public space rating
        places = ["parks","cafe","beaches","walking"]
        location = gmaps.geocode(f"{place}, NSW")[0]["geometry"]["location"]
        for place in places:
            # rate limiting sleep
            time.sleep(1)
            desirable_places = gmaps.places_nearby(keyword = place, location=location, radius=radius)['results']
            total.append(desirable_places)
        return total

    def get_place_photo(self,reference):
        # use photo reference
        pass

    '''
    This function takes a place and outputs the token score
    Get compound code -> council see if in csv 1, "compound_code":"467P+8R Woollahra, New South Wales"
    Get types -> check if any of these are in dataset 2. "types":[
            "park",
            "point_of_interest",
            "establishment"
         ]
    '''
    def get_token_score(self, place=None, types=None):
        score = 0
        s3 = boto3.resource('s3')
        bucket = s3.Bucket("exploroo-data")
        obj = bucket.Object(key="tokens.csv")
        response = obj.get()
        lines = response['Body'].read().decode('utf-8').splitlines(True)
        reader = csv.DictReader(lines)
        council_tokens = {k["council"].lower():k["tokens_council"] for k in reader}
        if place.lower() in council_tokens:
            score += int(council_tokens[place.lower()])
        # obj2 = bucket.Object(key="extra_tokens.csv")
        # response = obj2.get()
        # lines = response['Body'].read().decode('utf-8').splitlines(True)
        # reader = csv.DictReader(lines)
        # print(reader)

        # types_list = types.split(",")
        # #def intersection(lst1, lst2):
        # list(set(lst1) & set(lst2))
        return score

def lambda_handler2(event, context):
    try:
        if "location" in event["queryStringParameters"]:
            place = event["queryStringParameters"]["location"]
    except:
        return {
        'statusCode': 500,
        'body': 'Exception : location not included'
        }
    else:
        controller = Controller(local=False)
        return {
            'statusCode': 200,
            'body': json.dumps(controller.get_token_score(place=place))
        }

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    # return {
    #     "statusCode": 200,
    #     "body": json.dumps({
    #         "message": "hello world",
    #         # "location": ip.text.replace("\n", "")
    #     }),
    # }
    
    location = "Centennial Park, NSW"
    try:
        if "location" in event["queryStringParameters"]:
            place = event["queryStringParameters"]["location"]
    except:
        return {
        'statusCode': 500,
        'body': 'Exception : location not included'
        }
    else:
        controller = Controller(local=False)
        return {
            'statusCode': 200,
            'body': json.dumps(controller.get_places(place=location))
        }
if __name__ == "__main__":
    controller = Controller(local=True)
    controller.get_token_score("Ryde")
