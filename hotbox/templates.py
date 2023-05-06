from typing import Dict

from jinja2 import Template
from pydantic import BaseModel, StrictStr


class BaseTemplate(BaseModel):
    content: StrictStr
    inputs: Dict[StrictStr, StrictStr] = dict()

    def render(self) -> str:
        return Template(self.content).render(**self.inputs)


BASE_DOCKERFILE_TEMPLATE = """FROM {{ image }}

RUN cd /tmp && wget http://dl-cdn.alpinelinux.org/alpine/v3.14/releases/aarch64/alpine-minirootfs-3.14.9-aarch64.tar.gz
COPY inittab /tmp/overlay/etc/inittab
COPY interfaces /tmp/overlay/etc/network/interfaces
COPY start.sh /tmp/overlay/start.sh
COPY resolv.conf /tmp/overlay/etc/resolv.conf
COPY code /tmp/overlay/code
COPY entrypoint /entrypoint

WORKDIR /tmp/overlay/code

RUN {{ install }}

RUN {{ build }}

CMD ["/bin/bash", "/entrypoint"]
"""  # noqa: E501


class BaseDockerfileTemplate(BaseTemplate):
    content: StrictStr = BASE_DOCKERFILE_TEMPLATE


BASE_ENTRYPOINT_TEMPLATE = """#!/bin/bash

set -ex

dd if=/dev/zero of=/tmp/alpine-minirootfs-aarch64.ext4 bs=1M count={{ fs_size_mib }}
mkfs.ext4 /tmp/alpine-minirootfs-aarch64.ext4
mkdir -p /tmp/rootfs
mount -o loop /tmp/alpine-minirootfs-aarch64.ext4 /tmp/rootfs
tar xzf /tmp/alpine-minirootfs-3.14.9-aarch64.tar.gz -C /tmp/rootfs

# NOTE: disable this to remove networking from the image
sed -i "s/SUBNET_IP/$SUBNET_IP/g" /tmp/overlay/etc/network/interfaces
sed -i "s/GW_IP/$GW_IP/g" /tmp/overlay/etc/network/interfaces
sed -i "s/TAP_IP/$TAP_IP/g" /tmp/overlay/etc/network/interfaces
sed -i "s/MASK_LONG/$MASK_LONG/g" /tmp/overlay/etc/network/interfaces

# NOTE: disable this to remove networking from the image
sed -i "s/TAP_IP/$TAP_IP/g" /tmp/overlay/start.sh
sed -i "s/GW_IP/$GW_IP/g" /tmp/overlay/start.sh
sed -i "s/MASK_SHORT/\\$MASK_SHORT/g" /tmp/overlay/start.sh

cp -r /tmp/overlay/* /tmp/rootfs/

cat > /tmp/rootfs/prepare.sh <<EOF
passwd root -d root
apk update
apk add -u openrc ca-certificates haveged openssl udev
exit
EOF
chroot /tmp/rootfs/ /bin/sh /prepare.sh
rm /tmp/rootfs/prepare.sh

umount /tmp/rootfs
rm -rf /tmp/rootfs

mkdir -p /opt/code || :
cp /tmp/alpine-minirootfs-aarch64.ext4 /opt/code
"""


class BaseEntrypointTemplate(BaseTemplate):
    content: StrictStr = BASE_ENTRYPOINT_TEMPLATE


BASE_START_MICROVM_TEMPLATE = """echo "Starting sysfs and networking"
rc-service sysfs start
rc-service udev start
rc-service haveged start

# Set up network interface
# NOTE: remove this section to disable external networking
echo "Setting up eth0"
ifconfig eth0 up
echo "Setting up IP address"
ip addr add dev eth0 GW_IPMASK_SHORT
echo "Setting up default gateway"
ip route add default via TAP_IP
echo "Setting up eth0"
ip link set eth0 up
echo "Enable packet forwarding for internet access"
echo 1 > /proc/sys/net/ipv4/ip_forward
echo "Start networking"
rc-service networking start

# run the code in the microvm
# the firecracker compiler will place the code here
{{ entrypoint }}

# shutdown the microvm
reboot
"""


class BaseStartMicovmTemplate(BaseTemplate):
    content: StrictStr = BASE_START_MICROVM_TEMPLATE


BASE_INITTAB_TEMPLATE = """::sysinit:/sbin/openrc sysinit
::sysinit:/sbin/openrc boot
::wait:/sbin/openrc default

# NOTE: respawn can be used when the process is expected to terminate
ttyS0::once:/bin/ash /start.sh

::ctrlaltdel:/sbin/reboot
::shutdown:/sbin/openrc shutdown
"""


class BaseInitTabTemplate(BaseTemplate):
    content: StrictStr = BASE_INITTAB_TEMPLATE


BASE_INTERFACES_TEMPLATE = """#
#   /etc/network/interfaces
#
# We always want the loopback interface
#
auto lo
iface lo inet loopback
#
# Ethernet card setup: (broadcast and gateway are optional)
# NOTE: remove this section to disable external networking
#
auto eth0
iface eth0 inet static
    gateway TAP_IP
    address GW_IP
    netmask MASK_LONG
    network SUBNET_IP
    dns-nameservers 8.8.8.8
    # broadcast BROADCAST_IP
"""


class BaseInterfacesTemplate(BaseTemplate):
    content: StrictStr = BASE_INTERFACES_TEMPLATE


BASE_RESOLV_CONF_TEMPLATE = """nameserver 8.8.8.8
"""


class BaseResolvConfTemplate(BaseTemplate):
    content: StrictStr = BASE_RESOLV_CONF_TEMPLATE


BASE_RUN_APP_TEMPLATE = """#!/bin/bash -ex
# NOTE: This is a hack and will be replaced by some kind of productized code.

ARCH="$(uname -m)"

# Stop the firecracker process if it is already running
API_SOCKET="/root/fc-{{ app_name }}.socket"
rm -f $API_SOCKET

# Run firecracker
pkill -f "${API_SOCKET}" || true
firecracker --api-sock "${API_SOCKET}" &

# set up the kernel boot args and env vars
MASK_LONG="255.255.255.252"
MASK_SHORT="/30"

# Based on how many taps we have, we need to set up the IP addresses
# for the gateway and the tap interface. Pick the first available IP
# address in the range 192.168.0.0/16.
SUBNET_IP="192.168.0.0"
for FC_ID in $(seq 0 255); do
  GW_IP="$(printf '192.168.%s.%s' $(((4 * FC_ID + 1) / 256)) $(((4 * FC_ID + 1) % 256)))"
  TAP_IP="$(printf '192.168.%s.%s' $(((4 * FC_ID + 2) / 256)) $(((4 * FC_ID + 2) % 256)))"
  if ! ip addr show | grep -q $TAP_IP; then
    break
  fi
done

# NOTE: toggle eth0:on to eth0:off to disable networking
KERNEL_BOOT_ARGS="console=ttyS0 rw noapic reboot=k panic=1 pci=off nomodules random.trust_cpu=on random.hwrng_user_managed=on ip=${GW_IP}::${TAP_IP}:${MASK_LONG}::eth0:on"

# set up a tap network interface for the Firecracker VM to use
TAP_DEV="fc-$FC_ID-tap0"
ip link del "$TAP_DEV" 2> /dev/null || true
ip tuntap add "$TAP_DEV" mode tap
ip addr add "${TAP_IP}${MASK_SHORT}" dev "$TAP_DEV"
ip link set dev "$TAP_DEV" up

# Enable packet forwarding for internet access
DEVICE_NAME=$(ip route | grep default | awk '{print $5}')
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o $DEVICE_NAME -j MASQUERADE
iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $TAP_DEV -o $DEVICE_NAME -j ACCEPT

#
# Build and run image to generate rootfs
#
docker build -t {{ app_name }} /root/{{ app_name }}_image
OUTDIR=" /root/{{ app_name }}_outdir"
mkdir -p $OUTDIR
docker run --rm --privileged --env SUBNET_IP=$SUBNET_IP --env MASK_LONG=$MASK_LONG --env TAP_IP=$TAP_IP --env GW_IP=$GW_IP --env MASK_SHORT="$MASK_SHORT" -v $OUTDIR:/opt/code {{ app_name }}
ROOTFSDIR="$(readlink -f {{ app_name }}_fs)"
mv $OUTDIR/alpine-minirootfs-aarch64.ext4 $ROOTFSDIR
ROOTFS_PATH_ON_HOST="/root/{{ app_name }}_fs"

# get the MAC address of the tap device
FC_MAC="$(cat /sys/class/net/$TAP_DEV/address)"

# make a configuration file
cat <<EOF > fc-{{ app_name }}-config.json
{
  "boot-source": {
    "kernel_image_path": "vmlinux.bin",
    "boot_args": "$KERNEL_BOOT_ARGS"
  },
  "drives": [
    {
      "drive_id": "rootfs",
      "path_on_host": "$ROOTFS_PATH_ON_HOST",
      "is_root_device": true,
      "is_read_only": false
    }
  ],
  "network-interfaces": [
      {
          "iface_id": "eth0",
          "guest_mac": "$FC_MAC",
          "host_dev_name": "$TAP_DEV"
      }
  ],
  "machine-config": {
    "vcpu_count": {{ vcpu_count }},
    "mem_size_mib": {{ mem_size_mib }}
  }
}
EOF

# start firecracker
firecracker --no-api --config-file fc-{{ app_name }}-config.json
"""  # noqa: E501


class BaseRunAppTemplate(BaseTemplate):
    content: StrictStr = BASE_RUN_APP_TEMPLATE


BASE_EC2_USERDATA_TEMPLATE = """#!/bin/bash -ex

cd /root

# apt-get update -y and retry if it doesnt work
for i in {1..5}; do apt-get update -y && break || sleep 15; done

# Set a few variables
ARCH="$(uname -m)"
FC_VERSION="{{ firecracker_version }}"

# Download kernel
wget --no-clobber https://s3.amazonaws.com/spec.ccfc.min/img/${ARCH}/ubuntu/kernel/vmlinux.bin

# Download firecracker
wget --no-clobber https://github.com/firecracker-microvm/firecracker/releases/download/${FC_VERSION}/firecracker-${FC_VERSION}-${ARCH}.tgz
tar -xvf firecracker-${FC_VERSION}-${ARCH}.tgz
cp release-${FC_VERSION}-${ARCH}/firecracker-${FC_VERSION}-${ARCH} /usr/local/bin/firecracker
cp release-${FC_VERSION}-${ARCH}/jailer-${FC_VERSION}-${ARCH} /usr/local/bin/jailer
rm -rf firecracker-${FC_VERSION}-${ARCH}.tgz release-${FC_VERSION}-${ARCH}/

# Install docker
apt-get remove docker docker-engine docker.io containerd runc -y
apt-get install ca-certificates curl gnupg -y
mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update -y
apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

# Install hotbox
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa -y
apt install python3.10 python3.10-distutils -y
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
python3.10 -m pip install --upgrade pip
python3.10 -m pip install hotbox

# Run hotbox
hotbox server run --port 8420 &

# Install nginx
apt-get install nginx -y
rm /etc/nginx/sites-enabled/default
cat <<EOF > /etc/nginx/sites-enabled/hotbox
server {
    listen 8088;
    server_name _;
    location / {
        proxy_pass http://localhost:8420;
    }
}
EOF
systemctl restart nginx
"""  # noqa: E501


class BaseEc2UserdataTemplate(BaseTemplate):
    content: StrictStr = BASE_EC2_USERDATA_TEMPLATE
