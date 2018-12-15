#Author: Luis Mayorga
#Description: Mark Images and Ec2 Instances for Decomission
from __future__ import print_function
import json
import boto3
from datetime import datetime, timedelta


def get_outdated_images():
  outdated_images = set()
  ec2 = boto3.resource('ec2')
  images = ec2.images.filter(Owners=['self'])

  for image in images:
      created_at = datetime.strptime(
            image.creation_date,
            "%Y-%m-%dT%H:%M:%S.000Z",
      )

      if created_at <  datetime.now() - timedelta(30):
          outdated_images.add(image.id)
  return outdated_images

def set_tags_for_decommission(list_images):
  for image_id in list_images:
      ec2 = boto3.resource('ec2')
      image = ec2.Image(image_id)
      #NOTE: ReadyToDecomission Tag is overwritten if manually changed 
      image.create_tags(DryRun=False,Tags=[
        {
            'Key': 'ReadyToDecomission',
            'Value': 'True'
        },
    ]
)

def get_ec2_instances_with_decomission_source_ami():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.all()
    outdated_images = get_outdated_images()
    for instance in instances:
        if instance.image_id in outdated_images:
            print("I am instance %s " % instance.id)
            print("from source_id %s" % instance.image_id)
            #TODO: Tag the Instance
            #TODO: Notify To Owners


def lambda_handler(event, context):
    
    list_image_ids  = get_outdated_images()
    set_tags_for_decommission(list_image_ids)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }