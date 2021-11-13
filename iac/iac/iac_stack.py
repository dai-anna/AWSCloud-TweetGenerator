from aws_cdk import (
    core as cdk,
    aws_batch,
    aws_ec2,
)

class IacStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = aws_ec2.Vpc(self, "main-vpc")
        batch_compute_resources = aws_batch.ComputeResources(aws_ec2.Vpc.from_lookup(self, "main-vpc"))
        batch_compute_env = aws_batch.ComputeEnvironment(self, 'batch-compute-env', batch_compute_resources)
        pass
    pass