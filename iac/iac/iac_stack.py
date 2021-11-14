from aws_cdk import (
    core as cdk,
    aws_batch,
    aws_ec2,
    aws_ecs,
    aws_s3,
    aws_events,
    aws_events_targets,
)
import os 

class IacStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        bucket = aws_s3.Bucket(
            self,
            id = "mainbucket",
        )
        vpc = aws_ec2.Vpc(
            self,
            id = "mainvpc",
            max_azs = 1
        )
        i_vpc = aws_ec2.Vpc.from_vpc_attributes(self,
            "main-ipvc", 
            availability_zones = [i.availability_zone for i in vpc.public_subnets], 
            vpc_id = vpc.vpc_id,
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
            maxv_cpus = 2,
            minv_cpus = 0,
            security_groups = [sg],
            type=aws_batch.ComputeResourceType("SPOT"),
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
        batch_job_container = aws_batch.JobDefinitionContainer(
            image = aws_ecs.RepositoryImage(image_name="moritzwilksch/dukerepo:datacollector"),
            memory_limit_mib = 512,
            #command = ,
            environment = {"API_TOKEN":os.getenv("API_TOKEN"), "BUCKET_NAME":bucket.bucketname}
        )
        batch_job_definition = aws_batch.JobDefinition(
            self,
            id = "batch_jd",
            container = batch_job_container,
        )
        
        schedule1 = aws_events.Schedule.cron(hour="3", minute="5")
        target1 = aws_events_targets.BatchJob(
            job_queue_arn = batch_queue.job_queue_arn,
            job_queue_scope = q_batch_compute_env.compute_environment,
            job_definition_arn = batch_job_definition.job_definition_arn,
            job_definition_scope = q_batch_compute_env.compute_environment,
            attempts = 2,
        )
        #schedule2 = aws_events.Schedule.cron(hour="6", minute="5")
        
        #target2 = aws_events_targets.BatchJob(
        #)
        
        cronjob1 = aws_events.Rule(
            self,
            id="cronjob1",
            schedule=schedule1,
            targets=[target1]
        )
        #cronjob2 = aws_events.Rule(
        #    self,
        #    id="cronjob2",
        #    schedule=schedule2,
        #    targets=[target2]
        #)
        
#        bucket.grant_read_write(
#            identity= ,
#            objects_key_pattern = {}
#        )
        pass
    pass
