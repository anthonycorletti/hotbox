from enum import Enum, unique
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


@unique
class HotboxKind(str, Enum):
    """HotboxKind is a type of api resource that Hotbox can manage."""

    ec2 = "ec2"
    fc_microvm = "fc_microvm"
    fc_tap = "fc_tap"
    fc_bridge = "fc_bridge"
    app = "app"


@unique
class HotboxVersion(str, Enum):
    """HotboxVersion is the version of the Hotbox API."""

    v0alpha0 = "v0alpha0"


@unique
class Ec2MetalType(str, Enum):
    """Ec2MetalType is the type of EC2 instance to use for Hotbox."""

    a1_metal = "a1.metal"
    i3_metal = "i3.metal"
    g4dn_metal = "g4dn.metal"


class HotboxSpec(BaseModel):
    kind: HotboxKind
    version: HotboxVersion


class HotboxAwsSpec(HotboxSpec):
    region: str


class HotboxEc2Spec(HotboxAwsSpec):
    image_id: Optional[str] = None
    key_name: str
    security_group_ids: List[str]
    instance_type: Ec2MetalType = Ec2MetalType.a1_metal
    min_count: int = 1
    max_count: int = 1
    monitoring_enabled: Dict[str, Any] = {"Enabled": False}
    block_device_mappings: List[Dict[str, Any]] = [
        {
            "DeviceName": "/dev/xvda",
            "Ebs": {"DeleteOnTermination": True, "VolumeSize": 8, "VolumeType": "gp2"},
        },
    ]

    def user_data(self, num_microvm: int = 1) -> str:
        # TODO: add jailer!
        return "\n".join(  # noqa: E501
            [
                "#!/bin/bash -x",
                "apt update -y",
                "apt install -y iperf3",
                "\n".join(
                    [
                        "sudo tee -a /etc/security/limits.conf <<EOL",
                        "$USER soft nproc 16384",
                        "$USER hard nproc 16384",
                        "EOL",
                    ]
                ),
                "sudo chmod 777 /dev/kvm",
                "sysctl -wq net.ipv4.conf.all.forwarding=1",
                "sysctl -wq net.ipv4.neigh.default.gc_thresh1=1024",
                "sysctl -wq net.ipv4.neigh.default.gc_thresh2=2048",
                "sysctl -wq net.ipv4.neigh.default.gc_thresh3=4096",
                "FC_FILE_PATH=$HOME/firecracker",
                "TMP_FOLDER='/tmp/tmpfc'",
                "TMP_ARCHIVE='/tmp/tmpfcrelease.tgz'",
                (
                    "wget 'https://github.com/firecracker-microvm/firecracker/"
                    "releases/download/v1.3.1/firecracker-v1.3.1-aarch64.tgz' "
                    "-O $TMP_ARCHIVE"
                ),
                "mkdir -p $TMP_FOLDER",
                "tar -xvf $TMP_ARCHIVE -C $TMP_FOLDER",
                (
                    "cp $TMP_FOLDER/release-v1.3.1-aarch64/firecracker-v1.3.1-aarch64"
                    " $FC_FILE_PATH"
                ),
                'rm -rf "$TMP_FOLDER"',
                'rm "$TMP_ARCHIVE"',
                "KERNEL_FILE_PATH=$HOME/vmlinux",
                (
                    'wget -q "https://s3.amazonaws.com/spec.ccfc.min/ci-artifacts/'
                    'kernels/aarch64/vmlinux-4.14.bin" -O $KERNEL_FILE_PATH'
                ),
                'ROOTFS_FILE_PATH="$HOME/rootfs.ext4"',
                'ROOTFS_KEY_PATH="$TEST_RES/rootfs.id_rsa"',
                (
                    'wget -q "https://s3.amazonaws.com/spec.ccfc.min/ci-artifacts/'
                    'disks/aarch64/ubuntu-20.04.ext4" -O $ROOTFS_FILE_PATH'
                ),
                (
                    'wget -q "https://s3.amazonaws.com/spec.ccfc.min/ci-artifacts/'
                    'disks/aarch64/ubuntu-20.04.id_rsa" -O $ROOTFS_KEY_PATH'
                ),
                "chmod 400 $ROOTFS_KEY_PATH",
            ]
        )


class HotboxFcMicrovmSpec(HotboxSpec):
    ...


class HotboxFcTapSpec(HotboxSpec):
    ...


class HotboxFcBridgeSpec(HotboxSpec):
    ...


class HotboxAppSpec(HotboxSpec):
    ...
