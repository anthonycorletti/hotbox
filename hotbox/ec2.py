from typing import Dict, List

import boto3

from hotbox.services import HotboxService
from hotbox.types import HotboxEc2Spec


class HotboxEc2Service(HotboxService):
    def __init__(self) -> None:
        super().__init__()
        self.aws_client = boto3.client

    def get_image_id(
        self,
        client: boto3.client,
        name: str = "ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-arm64-*",
        virtualization_type: str = "hvm",
        architecture: str = "arm64",
        root_device_type: str = "ebs",
    ) -> str:
        filters = [
            {
                "Name": "name",
                "Values": [name],
            },
            {"Name": "virtualization-type", "Values": [virtualization_type]},
            {"Name": "architecture", "Values": [architecture]},
            {"Name": "root-device-type", "Values": [root_device_type]},
            {"Name": "owner-id", "Values": ["099720109477"]},
        ]
        images = client.describe_images(Filters=filters)
        images_sorted = sorted(
            images["Images"],
            key=lambda x: x["CreationDate"],
            reverse=True,
        )
        return images_sorted[0]["ImageId"]

    def create(self, spec: HotboxEc2Spec) -> Dict:
        ec2_client = self.aws_client("ec2", region_name=spec.region)
        if not spec.image_id:
            spec.image_id = self.get_image_id(
                client=ec2_client,
            )
        return ec2_client.run_instances(
            ImageId=spec.image_id,
            KeyName=spec.key_name,
            InstanceType=spec.instance_type,
            MinCount=spec.min_count,
            MaxCount=spec.max_count,
            Monitoring=spec.monitoring_enabled,
            SecurityGroupIds=spec.security_group_ids,
            BlockDeviceMappings=spec.block_device_mappings,
            # UserData=spec.user_data(),
        )

    def get(self, region: str) -> Dict:
        ec2_client = self.aws_client("ec2", region_name=region)
        return ec2_client.describe_instances()

    def delete(self, ids: List[str], region: str) -> Dict:
        ec2_client = self.aws_client("ec2", region_name=region)
        return ec2_client.terminate_instances(InstanceIds=ids)


hb_ec2_service = HotboxEc2Service()
