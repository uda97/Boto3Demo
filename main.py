import boto3
from botocore.exceptions import ClientError
import configuration
import paramiko


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
    elif select_code == 11:
        print("condor_status...")
        condor_status()
    elif select_code == 12:
        print("cli_mode...")
        cli_mode()
    elif select_code == 13:
        print("list_security_groups...")
        list_security_groups()
    elif select_code == 14:
        print("authorize_security_groups_ingress...")
        authorize_security_ingress()
    elif select_code == 15:
        print("revoke security group ingress ...")
        revoke_security_ingress()
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
            group_name = instance['SecurityGroups'][0]['GroupName']
            group_id = instance['SecurityGroups'][0]['GroupId']

            print(f'[id] {instance_id}, '
                  f'[AMI] {image_id}, '
                  f'[type] {instance_type}, '
                  f'[monitoring state] {monitoring_state}, '
                  f'[state] {instance_state}, '
                  f'[security group_name] {group_name}, '
                  f'[security group_id] {group_id}')


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
        KeyName="cloud-test",
        SecurityGroupIds=['sg-08e97ebd07e63c82f'],
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
        print(f'Successfully reboot instance{instance_id}')
    except ClientError as e:
        print('Error', e)


def list_images():
    response = ec2.describe_images(
        Owners=['self', ],
    )

    for image in response['Images']:
        print(
            f"[ImageID] {image['ImageId']}, "
            f"[Name] {image.get('Name', 'N/A')}, "
            f"[OwnerID] {image['OwnerId']}")


def connect_to_ec2():
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(hostname=configuration.HOSTNAME, username=configuration.USER_NAME,
                           key_filename=configuration.KEY_FILE)
        print("connect success")
        return ssh_client
    except Exception as e:
        print(f"connect fail: {e}")
        return None


def condor_status():
    client = connect_to_ec2()

    if client is not None:
        try:
            stdin, stdout, stderr = client.exec_command("condor_status")
            print("STDOUT:", stdout.read().decode())
            print("STDERR:", stderr.read().decode())
        finally:
            client.close()
    else:
        print("cannot ssh to ec2 instance")


def cli_mode():
    client = connect_to_ec2()

    if client is not None:
        try:
            while True:
                input_command = input("[ec2-user@ip-172-31-32-88.ap-northeast-2.compute.internal] ")
                if input_command != "exit":
                    stdin, stdout, stderr = client.exec_command(input_command)
                    stdout.channel.recv_exit_status()
                    print(stdout.read().decode())
                else:
                    break
        finally:
            client.close()
    else:
        print("cannot ssh to ec2 instance")


def list_security_groups():
    response = ec2.describe_security_groups()

    for group in response['SecurityGroups']:
        print("----------------------------------------------------------------")

        print(f"[GroupId] {group.get('GroupId')}, "
              f"[GroupName] {group.get('GroupName')}, "
              f"[Description] {group.get('Description')}")

        print("---inbound---")

        for in_permission in group['IpPermissions']:
            from_port = in_permission.get('FromPort')
            ip_protocol = in_permission.get('IpProtocol')
            ip_ranges = in_permission.get('IpRanges')
            to_port = in_permission.get('ToPort')
            print(f"[FromPort] {from_port}, [IpProtocol] {ip_protocol}, [ToPort] {to_port}, [IpRanges] {ip_ranges}, ")

        print("---outbound---")

        for out_permission in group['IpPermissionsEgress']:
            from_port = out_permission.get('FromPort')
            ip_protocol = out_permission.get('IpProtocol')
            ip_ranges = out_permission.get('IpRanges')
            to_port = out_permission.get('ToPort')

            print(f"[FromPort] {from_port}, [IpProtocol] {ip_protocol}, [ToPort] {to_port}, [IpRanges] {ip_ranges}, ")


def authorize_security_ingress():
    try:
        group_id = input("Enter the 'GroupId': ")
        from_port = int(input("Enter the 'FromPort': "))
        to_port = int(input("Enter the 'ToPort': "))
        ip_protocol = input("Enter the 'IpProtocol'[tcp/udp]: ")
        cidr_ip = input("Enter the 'CidrIp'[0.0.0.0/0]: ")
        response = ec2.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': from_port,
                    'IpProtocol': ip_protocol,
                    'IpRanges': [
                        {
                            'CidrIp': cidr_ip,
                            'Description': 'SSH access from the CBNU',
                        },
                    ],
                    'ToPort': to_port,
                },
            ],
        )

        print(response.get("Return"))
    except ClientError as e:
        print(e)


def revoke_security_ingress():
    group_id = input("Enter the 'GroupId': ")
    from_port = int(input("Enter the 'FromPort': "))
    to_port = int(input("Enter the 'ToPort': "))
    ip_protocol = input("Enter the 'IpProtocol'[tcp/udp]: ")
    cidr_ip = input("Enter the 'CidrIp'[0.0.0.0/0]: ")

    response = ec2.revoke_security_group_ingress(
        GroupId=group_id,
        IpPermissions=[
            {
                'IpProtocol': ip_protocol,
                'FromPort': from_port,
                'ToPort': to_port,
                'IpRanges': [{'CidrIp': cidr_ip}]
            }
        ]
    )
    print(response.get("Return"))


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
            ------------------------------------------------------------
              11. condor_status               12. CLI mode
              13. list security groups        14. authorize security group ingress
              15. revoke security group ingress 
            ------------------------------------------------------------            ''')

        select_code = input("Enter an integer: ")
        try:
            select_code = int(select_code)
            switch(select_code)
        except ValueError:
            print("Invalid input")


if __name__ == "__main__":
    main()
