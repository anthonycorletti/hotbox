#!/bin/bash

apt update -y

apt install docker.io -y

ARCH="$(uname -m)"

# Download a linux kernel binary
wget --no-clobber https://s3.amazonaws.com/spec.ccfc.min/img/quickstart_guide/${ARCH}/kernels/vmlinux.bin

# Download a rootfs
wget --no-clobber https://s3.amazonaws.com/spec.ccfc.min/ci-artifacts/disks/${ARCH}/ubuntu-18.04.ext4

# Download the ssh key for the rootfs
wget --no-clobber https://s3.amazonaws.com/spec.ccfc.min/ci-artifacts/disks/${ARCH}/ubuntu-18.04.id_rsa

# Set user read permission on the ssh key
chmod 400 ./ubuntu-18.04.id_rsa

# Clone the firecracker repository
git clone https://github.com/firecracker-microvm/firecracker

docker pull public.ecr.aws/firecracker/fcuvm:v52
./firecracker/tools/devtool build

API_SOCKET="./firecracker.socket"

rm -f $API_SOCKET

# Run firecracker
./firecracker/build/cargo_target/${ARCH}-unknown-linux-musl/debug/firecracker --api-sock "${API_SOCKET}" &

TAP_DEV="tap0"
TAP_IP="172.16.0.2"
MASK_SHORT="/30"

# Setup network interface
ip link del "$TAP_DEV" 2> /dev/null || true
ip tuntap add dev "$TAP_DEV" mode tap
ip addr add "${TAP_IP}${MASK_SHORT}" dev "$TAP_DEV"
ip link set dev "$TAP_DEV" up

# Enable ip forwarding
sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

# Set up microVM internet access
iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE || true
iptables -D FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT || true
iptables -D FORWARD -i tap0 -o eth0 -j ACCEPT || true
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -I FORWARD 1 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -I FORWARD 1 -i tap0 -o eth0 -j ACCEPT

API_SOCKET="./firecracker.socket"
LOGFILE="./firecracker.log"

# Create log file
touch $LOGFILE

# Set log file
curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"log_path\": \"${LOGFILE}\",
        \"level\": \"Debug\",
        \"show_level\": true,
        \"show_log_origin\": true
    }" \
    "http://localhost/logger"

KERNEL="./vmlinux.bin"
KERNEL_BOOT_ARGS="console=ttyS0 reboot=k panic=1 pci=off"

ARCH=$(uname -m)

if [ ${ARCH} = "aarch64" ]; then
    KERNEL_BOOT_ARGS="keep_bootcon ${KERNEL_BOOT_ARGS}"
fi

# Set boot source
curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"kernel_image_path\": \"${KERNEL}\",
        \"boot_args\": \"${KERNEL_BOOT_ARGS}\"
    }" \
    "http://localhost/boot-source"

ROOTFS="./ubuntu-18.04.ext4"

# Set rootfs
curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"drive_id\": \"rootfs\",
        \"path_on_host\": \"${ROOTFS}\",
        \"is_root_device\": true,
        \"is_read_only\": false
    }" \
    "http://localhost/drives/rootfs"

# The IP address of a guest is derived from its MAC address with
# `fcnet-setup.sh`, this has been pre-configured in the guest rootfs. It is
# important that `TAP_IP` and `FC_MAC` match this.
FC_MAC="$(cat /sys/class/net/tap0/address)"

# Set network interface
curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"iface_id\": \"net1\",
        \"guest_mac\": \"$FC_MAC\",
        \"host_dev_name\": \"$TAP_DEV\"
    }" \
    "http://localhost/network-interfaces/net1"

# API requests are handled asynchronously, it is important the configuration is
# set, before `InstanceStart`.
sleep 1

# Start microVM
curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"action_type\": \"InstanceStart\"
    }" \
    "http://localhost/actions"

# ssh -i ./ubuntu-18.04.id_rsa 172.16.0.1
