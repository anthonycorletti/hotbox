from typing import Any, Dict, List


class MockEc2Service:
    def describe_images(self, Filters: Dict[str, List[Dict]]) -> Dict:
        return {
            "Images": [
                {
                    "Architecture": "arm64",
                    "CreationDate": "2020-06-11T00:00:00.000Z",
                    "ImageId": "ami-0000",
                    "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/"
                    "ubuntu-bionic-18.04-arm64-server-20200610",
                    "ImageType": "machine",
                    "Public": True,
                    "OwnerId": "099720109477",
                    "Platform": None,
                    "State": "available",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/sda1",
                            "Ebs": {
                                "DeleteOnTermination": True,
                                "SnapshotId": "snap-0000",
                                "VolumeSize": 8,
                                "VolumeType": "gp2",
                                "Encrypted": False,
                            },
                        }
                    ],
                    "Description": "Canonical, Ubuntu, 18.04 LTS, amd64 "
                    "bionic image build on 2020-06-10",
                    "EnaSupport": True,
                    "Hypervisor": "xen",
                    "ImageOwnerAlias": "099720109477",
                    "Name": "ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-arm64-*",
                    "RootDeviceName": "/dev/sda1",
                    "RootDeviceType": "ebs",
                    "SriovNetSupport": "simple",
                    "VirtualizationType": "hvm",
                }
            ]
        }

    def run_instances(
        self,
        **kwargs: Any,
    ) -> Dict:
        return {}

    def describe_instances(self) -> Dict:
        return {}

    def terminate_instances(self, InstanceIds: List[str]) -> Dict:
        return {}
