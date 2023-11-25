import boto3

ec2 = boto3.client('ec2')


def switch(select_code):
    if select_code == 1:
        list_instances()
    elif select_code == 2:
        available_zones()
    elif select_code == 3:
        return 3
    elif select_code == 4:
        available_regions()
    elif select_code == 5:
        return 5
    elif select_code == 6:
        return 6
    elif select_code == 7:
        return 7
    elif select_code == 8:
        return 8
    elif select_code == 99:
        print("Exiting...")
        exit()
    else:
        print("Invalid Input, Exiting...")
        exit()


def list_instances():
    response = ec2.describe_instances()
    print('Listing instances...')
    # print(response)
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
    # Retrieves all regions/endpoints that work with EC2
    response = ec2.describe_regions()
    # print('Regions:', response['Regions'])
    for each_response in response['Regions']:
        s1 = each_response['RegionName']
        s2 = each_response['Endpoint']
        print(f'[region]{s1:>15}, [Endpoint] {s2}')


def available_regions():
    # Retrieves availability zones only for region of the ec2 object
    response = ec2.describe_availability_zones()
    # print('Availability Zones:', response['AvailabilityZones'])
    for each_response in response['AvailabilityZones']:
        s1 = each_response['ZoneId']
        s2 = each_response['RegionName']
        s3 = each_response['ZoneName']
        print(f'[id] {s1:10}, [region] {s2:10}, [zone] {s3:10}')


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
        print("Enter an integer: ")

        select_code = input()
        try:
            select_code = int(select_code)
            switch(select_code)
        except ValueError:
            print("Invalid input")


if __name__ == "__main__":
    main()
