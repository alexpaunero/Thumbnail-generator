import json
import boto3
from io import BytesIO
from PIL import Image, ImageOps
import os

s3 = boto3.client('s3')
img_size = int(os.environ['THUMBNAIL_SIZE'])

def thumbnail_sbs(event, context):
    print('It works.')
    print("EVENT:::", event)
    print("CONTEXT:::", context)
    
    #Extract bucket name
    bucket = event['Records'][0]['s3']['bucket']['name']
    print(bucket)
    #Extract filename
    filename = event['Records'][0]['s3']['object']['key']
    print(filename)
    print(filename.endswith('.png'))
    #Extract size
    size = event['Records'][0]['s3']['object']['size']
    print(size)

    #Check that file is already a thumbnail
    if(filename.endswith('_thumbnail.png')):
        print('File: ' + filename + ' is already a thumbnail. Unable to convert file.')
        body = {
        "message": "Your function executed successfully! Op. 0",
        "input": event,
    }
        return {"statusCode": 200, "body": json.dumps(body)}
    #Check if file is not a PNG
    elif(not filename.endswith('.png')):
        print('File: ' + filename + ' is not a PNG file. Unable to convert file to thumbnail.')
        body = {
        "message": "Your function executed successfully! Op. 1",
        "input": event,
    }
        return {"statusCode": 200, "body": json.dumps(body)}
    #Proceed to generate thumbnail
    else:
        thumbnail_filename = generate_thumbnail_filename(filename)
        print(thumbnail_filename)
        image = get_s3_image(bucket, filename)
        print('get_s3_image correctly completed')
        thumbnail = create_thumbnail_file(image)
        print('Thumbnail generated correctly.')
        url = store_thumbnail_in_s3(thumbnail, bucket, thumbnail_filename)
        print(url)
        body = {
        "message": "Your function executed successfully! Op. 2",
        "input": event,
        }
        return {"statusCode": 200, "body": json.dumps(body)}


def generate_thumbnail_filename(key):
    key_split = key.rsplit('.', 1)
    return key_split[0] + "_thumbnail.png"

def get_s3_image(bucket, key):
    print('Getting image ' + key + ' from S3 bucket ' + bucket)
    response = s3.get_object(Bucket=bucket, Key=key)
    print('Response: ')
    print(response)
    imagecontent = response['Body'].read()
    print(imagecontent)
    file = BytesIO(imagecontent)
    print(file)
    img = Image.open(file)
    print(img)
    return img

def create_thumbnail_file(image):
    return ImageOps.fit(image, (img_size, img_size), Image.Resampling.LANCZOS)

def store_thumbnail_in_s3(thumbnail, bucket, key):
    print('Storing thumbnail to s3.')
    out_thumbnail = BytesIO()
    thumbnail.save(out_thumbnail, 'PNG')
    out_thumbnail.seek(0)
    response = s3.put_object(
        ACL = 'public-read',
        Body = out_thumbnail,
        Bucket = bucket,
        ContentType = 'image/png',
        Key = key
    )
    print(response)
    url = '{}/{}/{}'.format(s3.meta.endpoint_url, bucket, key)
    return url