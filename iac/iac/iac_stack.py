from aws_cdk import (
    core as cdk,
    aws_batch,
    aws_ec2,
)

class IacStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
    
        vpc = aws_ec2.Vpc(
            self,
            id = "mainvpc",
            max_azs = 1
        )
        i_vpc = aws_ec2.Vpc.from_vpc_attributes(self,
            "main-ipvc", 
            availability_zones = [i.availability_zone for i in vpc.public_subnets], 
            vpc_id = "mainvpc",
            public_subnet_ids = [i.subnet_id for i in vpc.public_subnets],
        )
        sg = aws_ec2.SecurityGroup(
            self,
            id = "allsgid",
            vpc = i_vpc,
            #allow_all_outbound = True,
        )
        batch_compute_resources = aws_batch.ComputeResources(
            vpc = i_vpc,
            desiredv_cpus = 1,
            maxv_cpus = 1,
            minv_cpus = 0,
            security_groups = [sg],
        )
        batch_compute_env = aws_batch.ComputeEnvironment(
            scope=self,
            id='batch-compute-env',
            compute_resources=batch_compute_resources,
        )
        q_batch_compute_env = aws_batch.JobQueueComputeEnvironment(
            compute_environment = aws_batch.ComputeEnvironment.from_compute_environment_arn(
                self,
                id="i-compute-env",
                compute_environment_arn = batch_compute_env.compute_environment_arn,
            ),
            order = 1,
        )
        batch_queue = aws_batch.JobQueue(
            self,
            "batch-queue",
            compute_environments = [q_batch_compute_env],
        )
        pass
    pass

#availability_zone