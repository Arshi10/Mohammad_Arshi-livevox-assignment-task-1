#This module is having all relevent functions
#which is being called by test cases

import boto3
import os
from datetime import datetime
from datetime import timedelta

aws_access_key_id=os.environ['aws_access_key_id']
aws_secret_access_key=os.environ['aws_secret_access_key']


class Aws_Functions():

    #It will return the asg instance list
    def get_asg_instances(self, asg_name):
        asg_instances = []
        client = boto3.client('autoscaling', aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key, region_name='ap-south-1')
        response = client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])

        if 'AutoScalingGroups' in response:
            asg = response['AutoScalingGroups'][0]
            asg_instances = asg['Instances']

        return asg_instances

    #For validating the desire counts of instances
    def validate_desired_running_count(self, asg_name):
        asg_instances = self.get_asg_instances(asg_name)
        desired_count = len(asg_instances)
        running_count = sum(1 for instance in asg_instances if instance['LifecycleState'] == 'InService')

        assert desired_count == running_count, "desired asg count not matching" \
                                                "with running asg count"


    #For validating availibility zones
    def validate_availability_zones(self, asg_name):
        asg_instances = self.get_asg_instances(asg_name)
        availability_zones = set(
            instance['AvailabilityZone'] for instance in asg_instances if instance['LifecycleState'] == 'InService')

        assert len(availability_zones) >= len(asg_instances), "count mismatch in availability zone"

    #For validiating security groups, Imageid and VPC
    def validate_security_group_image_vpc(self, asg_name):
        asg_instances = self.get_asg_instances(asg_name)
        security_groups = set(instance['SecurityGroups'][0]['GroupId'] for instance in asg_instances if
                              instance['LifecycleState'] == 'InService')
        print("asg_instances", asg_instances)
        flag = 0
        if len(asg_instances) >= 1:
            try:
                vpc_id = asg_instances[0]['VpcId']
                image_id = asg_instances[0]['ImageId']
                flag = 1
            except:
                pass
        if flag == 1:
            assert len(security_groups) == 1 and all(
                instance['ImageId'] == image_id and instance['VpcId'] == vpc_id for instance in asg_instances if
                instance['LifecycleState'] == 'InService'), "SecuirtyGroup, ImageID and VPCID not running on same ASG instances"

    #for getting instance uptime
    def get_instance_uptime(self, instance):
        launch_time = instance['LaunchTime']
        now = datetime.now(launch_time.tzinfo)
        uptime = now - launch_time
        return uptime

    #for getting longest runtime instance
    def get_longest_running_instance(self, asg_name):
        asg_instances = self.get_asg_instances(asg_name)
        longest_uptime = None
        longest_instance = None

        for instance in asg_instances:
            if instance['LifecycleState'] == 'InService':
                uptime = self.get_instance_uptime(instance)
                if longest_uptime is None or uptime > longest_uptime:
                    longest_uptime = uptime
                    longest_instance = instance

        return longest_instance

    # for getting next action of asg and elapsed time
    def get_next_scheduled_action(self, asg_name):
        client = boto3.client('autoscaling', aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key, region_name='ap-south-1')
        response = client.describe_scheduled_actions(AutoScalingGroupName=asg_name)

        now = datetime.now()
        next_action_time = None

        for action in response['ScheduledUpdateGroupActions']:
            action_time = action['StartTime']
            if now < action_time and (next_action_time is None or action_time < next_action_time):
                next_action_time = action_time
                next_action_name = action['ScheduledActionName']

        if next_action_time:
            time_until_next_action = next_action_time - now
            print("next action name is : ", next_action_name)
            print("time elapsed: ", time_until_next_action)
        else:
            print("No upcoming scheduled actions.")


    #getting the count of instances launched and terminated
    def get_instances_launched_terminated(self, asg_name):
        client = boto3.client('cloudwatch', aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key, region_name='ap-south-1')

        now = datetime.now()
        start_of_day = datetime(year=now.year, month=now.month, day=now.day)
        end_of_day = start_of_day + timedelta(days=1)

        response = client.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'instances_launched',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/AutoScaling',
                            'MetricName': 'GroupDesiredCapacity',
                            'Dimensions': [
                                {
                                    'Name': 'AutoScalingGroupName',
                                    'Value': asg_name
                                }
                            ]
                        },
                        'Period': 3600,
                        'Stat': 'Sum',
                    },
                    'ReturnData': True,
                },
                {
                    'Id': 'instances_terminated',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/AutoScaling',
                            'MetricName': 'GroupTotalInstances',
                            'Dimensions': [
                                {
                                    'Name': 'AutoScalingGroupName',
                                    'Value': asg_name
                                }
                            ]
                        },
                        'Period': 3600,
                        'Stat': 'Sum',
                    },
                    'ReturnData': True,
                }
            ],
            StartTime=start_of_day,
            EndTime=end_of_day,
        )

        instances_launched = response.get('MetricDataResults', [{}])[0].get('Values', [0])[0]
        instances_terminated = response.get('MetricDataResults', [{}])[1].get('Values', [0])[0]

        return instances_launched, instances_terminated
