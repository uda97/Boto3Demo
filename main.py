import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')


def switch(select_code):
    if select_code == 1:
        list_instances()
    elif select_code == 2:
        available_zones()
    elif select_code == 3:
        input_instance_id = input('Enter instance id: ')
        start_instance(input_instance_id)
    elif select_code == 4:
        available_regions()
    elif select_code == 5:
        input_instance_id = input('Enter instance id: ')
        stop_instance(input_instance_id)
    elif select_code == 6:
        input_ami_id = input('Enter ami id: ')
        create_instance(input_ami_id)
    elif select_code == 7:
        input_instance_id = input('Enter instance id: ')
        reboot_instance(input_instance_id)
    elif select_code == 8:
        print("Listing images...")
        list_images()
    elif select_code == 99:
        print("Exiting...")
        exit()
    else:
        print("Invalid Input, Exiting...")
        exit()


def list_instances():
    response = ec2.describe_instances()
    print('Listing instances...')

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance.get('InstanceId')
            image_id = instance.get('ImageId')
            instance_type = instance.get('InstanceType')
            monitoring_state = instance['Monitoring']['State']
            instance_state = instance['State']['Name']

            print(f'[id] {instance_id}, '
                  f'[AMI] {image_id}, '
                  f'[type] {instance_type}, '
                  f'[monitoring state] {monitoring_state}, '
                  f'[state] {instance_state}')


def available_zones():
    response = ec2.describe_regions()
    for each_response in response['Regions']:
        s1 = each_response.get('RegionName')
        s2 = each_response.get('Endpoint')
        print(f'[region]{s1:>15}, [Endpoint] {s2}')


def start_instance(instance_id):
    print(f'Starting ... {instance_id}')

    # verify permissions
    try:
        ec2.start_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    # run without dryrun
    try:
        response = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
        server_status = response.get('StartingInstances')[0].get('PreviousState').get('Name')
        if server_status == 'stopped':
            print(f'Successfully started instance{instance_id}')
        if server_status == 'running':
            print(f'failure started instance: {instance_id} is already running')
    except ClientError as e:
        print(e)


def available_regions():

    response = ec2.describe_availability_zones()

    for each_response in response['AvailabilityZones']:
        s1 = each_response.get('ZoneId')
        s2 = each_response.get('RegionName')
        s3 = each_response.get('ZoneName')
        print(f'[id] {s1:10}, [region] {s2:10}, [zone] {s3:10}')


def stop_instance(instance_id):
    print(f'Stopping ... {instance_id}')

    # verify permissions
    try:
        ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    # stop without dryrun
    try:
        response = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
        server_status = response.get('StoppingInstances')[0].get('PreviousState').get('Name')
        if server_status == 'running':
            print(f'Successfully stopped instance{instance_id}')
        if server_status == 'stopped':
            print(f'failure stopped instance: {instance_id} is already stopped')
    except ClientError as e:
        print(e)


def create_instance(input_ami_id):

    response = ec2.run_instances(
        ImageId=input_ami_id,
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        KeyName="cloud_test",
    )

    instance_id = response['Instances'][0]['InstanceId']

    print(f"Created EC2 instance with ID: {instance_id}")


def reboot_instance(instance_id):
    print(f'Rebooting ... {instance_id}')

    try:
        ec2.reboot_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            print("You don't have permission to reboot instances.")
            raise

    try:
        response = ec2.reboot_instances(InstanceIds=[instance_id], DryRun=False)
        print(f'Successfully stopped instance{instance_id}')
    except ClientError as e:
        print('Error', e)


def list_images():
    response = ec2.describe_images(
        Owners=['self',],
    )

    for image in response['Images']:
        print(
            f"[ImageID] {image['ImageId']}, "
            f"[Name] {image.get('Name', 'N/A')}, "
            f"[OwnerID] {image['OwnerId']}")


def main():
    while True:
        print(f'''
    
            ------------------------------------------------------------
                       Amazon AWS Control Panel using SDK               
            ------------------------------------------------------------
              1. list instance                2. available zones
              3. start instance               4. available regions             
              5. stop instance                6. create instance         
              7. reboot instance              8. list images         
                                              99. quit          
              ------------------------------------------------------------            ''')

        select_code = input("Enter an integer: ")
        try:
            select_code = int(select_code)
            switch(select_code)
        except ValueError:
            print("Invalid input")


if __name__ == "__main__":
    main()
