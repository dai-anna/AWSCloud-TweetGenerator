#This is the main code to edit to modify the stack structure.
from aws_cdk import (
    core as cdk,
    aws_batch,
    aws_ec2,
    aws_ecs,
    aws_s3,
    aws_events,
    aws_iam,
    aws_events_targets,
    aws_stepfunctions,
    aws_stepfunctions_tasks,
    aws_lambda,
    aws_ecr,
)
import os 

class IacStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        bucket = aws_s3.Bucket(
            self,
            id = "mainbucket",
        )
        iamrole = aws_iam.Role(
            self,
            id = "iac_iamrole",
            assumed_by = aws_iam.ServicePrincipal("batch.amazonaws.com"),
            managed_policies = [
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSBatchServiceRole"),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
            ]
        )
        iamrole_ecs = aws_iam.Role(
            self,
            id = "iacecs_iamrole",
            assumed_by = aws_iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies = [
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role"),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
            ]
        )
        
        # iamrole_sfn =aws_iam.Role(
        #     self,
        #     id = "iacsfn_iamrole",
        #     assumed_by = aws_iam.ServicePrincipal("ec2.amazonaws.com"),
        #     managed_policies = [
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role"),
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
        #     ]
        # )
        
        ecs_instance_profile = aws_iam.CfnInstanceProfile(
            self,
            id = "ecsInstanceProfile",
            roles = [
                iamrole_ecs.role_name
            ]
        )
        vpc = aws_ec2.Vpc(#Only one public subnet, in only one availability zone, in one region. 
            self,
            id = "mainvpc",
            max_azs = 1,
            subnet_configuration = [
                aws_ec2.SubnetConfiguration(
                    name = "public_subnet1",
                    subnet_type = aws_ec2.SubnetType("PUBLIC")
                )
            ]
        )
        i_vpc = aws_ec2.Vpc.from_vpc_attributes(self, #this was created to be passed into sg and batch_compute_resource. may have been unnecessary and just the vpc may have sufficed
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
        
        # move schedulers to before lambda and change to dict
        schedulers = {
            "hashtagtime":aws_events.Schedule.cron(hour="1", minute="31"),
            "tweettime":aws_events.Schedule.cron(hour="3", minute="50"),
        }
        
        # create cronjob for hashtag scrape
        # add lambda function for hashtags
        hashtag_lambda = aws_lambda.DockerImageFunction(
            self,
            id = "hashtag_lambda",
            code = aws_lambda.DockerImageCode(
                repository = aws_ecr.Repository.from_repository_name(
                    self, 
                    "hashtag_repo",
                    "dukerepo",
                )
            )
        )
        
        cronhash = aws_events.Rule(
            self,
            id="cronjob_hashtag",
            schedule = schedulers["hashtagtime"],
            targets = aws_events_targets.LambdaFunction(
                handler = hashtag_lambda,
            )
        )
        
        batch_compute_resources = aws_batch.ComputeResources(
            vpc = i_vpc,
            desiredv_cpus = 1,
            maxv_cpus = 2,
            minv_cpus = 0,
            security_groups = [sg],
            type=aws_batch.ComputeResourceType("SPOT"),
            bid_percentage = 60,
            instance_role = ecs_instance_profile.attr_arn,
            instance_types = [aws_ec2.InstanceType("m3.medium")],
        )
        batch_compute_env = aws_batch.ComputeEnvironment(
            scope=self,
            id='batch-compute-env',
            compute_resources=batch_compute_resources,
            #service_role = iamrole.role_arn,
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
        #updating below
        container_images = ["moritzwilksch/dukerepo:datacollector", "moritzwilksch/dukerepo:modeltrain"]
        batch_job_containers = [
            aws_batch.JobDefinitionContainer(
                image = aws_ecs.RepositoryImage(image_name = ci),
                memory_limit_mib = 512,
                environment = {"API_TOKEN":os.getenv("API_TOKEN"), "BUCKET_NAME":bucket.bucket_name}
            ) for ci in container_images
        ]
        batch_job_definitions = [
            aws_batch.JobDefinition(
                self,
                id = "batch_jd" + str(i+1),
                container = bjc,
            ) for i,bjc in enumerate(batch_job_containers)
        ]
        
        # tweet_target = aws_events_targets.BatchJob(
        #     job_queue_arn = batch_queue.job_queue_arn,
        #     job_queue_scope = q_batch_compute_env.compute_environment,
        #     job_definition_arn = batch_job_definitions[0].job_definition_arn,
        #     job_definition_scope = q_batch_compute_env.compute_environment,
        #     attempts = 2,
        #     )
            
        
        # dependencies = aws_stepfunctions_tasks.BatchJobDependency(
        #     job_id=dc_job."AWS_BATCH_JOB_ID", 
        #     type=None)
            
        # tweet scrape and training cronjob
        crontweet = aws_events.Rule(
            self,
            id="cronjob_tweet",
            schedule=schedulers["tweettime"],
        )
        
        datacollection_job = aws_stepfunctions_tasks.BatchSubmitJob(
            self,
            id="datacollection_job",
            job_definition_arn = batch_job_definitions[0].job_definition_arn,
            job_name = "dc_job",
            job_queue_arn = batch_queue.job_queue_arn,
            attempts = 2
            )
        
        modeltrain_job = aws_stepfunctions_tasks.BatchSubmitJob(
            self,
            id="modeltrain_job",
            job_definition_arn = batch_job_definitions[1].job_definition_arn,
            job_name = "mt_job",
            job_queue_arn = batch_queue.job_queue_arn,
            attempts = 2
            )
        
    
        definition = datacollection_job\
            .next(aws_stepfunctions.Choice(self, "choice")
                .when(aws_stepfunctions.Condition.string_equals("$.status", "SUCCESS"), modeltrain_job)
            )
        
        state_machine = aws_stepfunctions.StateMachine(
            self, 
            "state_machine",
            definition=definition,
            # role=iamrole_sfn
        )
        
        crontweet.add_target(aws_events_targets.SfnStateMachine(state_machine))
        
        bucket.grant_read_write(# I don't know if this contributes anything
            identity= iamrole,
        )
        bucket.grant_read_write(
            identity = iamrole_ecs
        )
        pass
    pass