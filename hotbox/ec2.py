from typing import Dict, List

import boto3

from hotbox._types import Ec2Spec
from hotbox.templates import BaseEc2UserdataTemplate


class Ec2Service:
    def ec2_client(self, region_name: str) -> boto3.client:
        return boto3.client("ec2", region_name=region_name)  # pragma: no cover

    def get_image_id(
        self,
        ec2_client: boto3.client,
        name: str = "ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-arm64-*",
        virtualization_type: str = "hvm",
        architecture: str = "arm64",
        root_device_type: str = "ebs",
        owner_id: str = "099720109477",
    ) -> str:
        filters = [
            {"Name": "name", "Values": [name]},
            {"Name": "virtualization-type", "Values": [virtualization_type]},
            {"Name": "architecture", "Values": [architecture]},
            {"Name": "root-device-type", "Values": [root_device_type]},
            {"Name": "owner-id", "Values": [owner_id]},
        ]
        images = ec2_client.describe_images(Filters=filters)
        images_sorted = sorted(
            images["Images"],
            key=lambda x: x["CreationDate"],
            reverse=True,
        )
        return images_sorted[0]["ImageId"]

    def _template_userdata(
        self,
        firecracker_version: str,
    ) -> str:
        return BaseEc2UserdataTemplate(
            inputs={
                "firecracker_version": firecracker_version,
            }
        ).render()

    def create(self, spec: Ec2Spec, firecracker_version: str) -> Dict:
        ec2_client = self.ec2_client(region_name=spec.region)
        return ec2_client.run_instances(
            ImageId=self.get_image_id(ec2_client=ec2_client),
            KeyName=spec.key_name,
            InstanceType=spec.instance_type,
            MinCount=spec.min_count,
            MaxCount=spec.max_count,
            Monitoring=spec.monitoring_enabled,
            SecurityGroupIds=spec.security_group_ids,
            BlockDeviceMappings=spec.block_device_mappings,
            TagSpecifications=spec.tag_specifications,
            UserData=self._template_userdata(firecracker_version=firecracker_version),
        )

    def get(self, region: str) -> Dict:
        ec2_client = self.ec2_client(region_name=region)
        return ec2_client.describe_instances()

    def delete(self, ids: List[str], region: str) -> Dict:
        ec2_client = self.ec2_client(region_name=region)
        return ec2_client.terminate_instances(InstanceIds=ids)


ec2_svc = Ec2Service()
