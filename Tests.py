#This module is having test cases

import AwsModules as AM


class Test_cases():
    def __init__(self, **kwargs):
        self.asg_name = kwargs.get("asg_name")
        self.Aws = AM.Aws_Functions()

    #Test A as mentioned in the git hub
    def Test_A(self):
        asg_instances = self.Aws.validate_desired_running_count(self.asg_name)
        self.Aws.validate_availability_zones(self.asg_name)
        self.Aws.validate_security_group_image_vpc(self.asg_name)

        if asg_instances is not None:
            for instance in asg_instances:
                uptime = self.Aws.get_instance_uptime(instance)
                print("instance:  having uptime:  ".format(instance['InstanceId'], uptime))

            longest_instance = self.Aws.get_longest_running_instance(self.asg_name)
            print(f'Longest running instance, {longest_instance}')


    # Test B as mentioned in the git hub
    def Test_B(self):
        self.Aws.get_next_scheduled_action(self.asg_name)
        instances_launched, instances_terminated = self.Aws.get_instances_launched_terminated(self.asg_name)
        print(f"Total instances launched today: {instances_launched}")
        print(f"Total instances terminated today: {instances_terminated}")












