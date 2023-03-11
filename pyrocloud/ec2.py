from typing import Dict, List

import boto3

from pyrocloud.services import PyroService
from pyrocloud.types import PyroEc2Spec


class PyroEc2Service(PyroService):
    def __init__(self) -> None:
        super().__init__()
        self.aws_client = boto3.client

    def create(self, spec: PyroEc2Spec) -> Dict:
        ec2_client = self.aws_client("ec2", region_name=spec.region)
        return ec2_client.run_instances(
            ImageId=spec.image_id,
            KeyName=spec.key_name,
            InstanceType=spec.instance_type,
            MinCount=spec.min_count,
            MaxCount=spec.max_count,
            Monitoring=spec.monitoring_enabled,
            SecurityGroupIds=spec.security_group_ids,
            BlockDeviceMappings=spec.block_device_mappings,
        )

    def get(self, region: str) -> Dict:
        ec2_client = self.aws_client("ec2", region_name=region)
        return ec2_client.describe_instances()

    def delete(self, ids: List[str], region: str) -> Dict:
        ec2_client = self.aws_client("ec2", region_name=region)
        return ec2_client.terminate_instances(InstanceIds=ids)


pyro_ec2_service = PyroEc2Service()
