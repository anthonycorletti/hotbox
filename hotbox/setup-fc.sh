#!/bin/bash

apt update -y

ARCH="$(uname -m)"
FC_VERSION="v1.3.1"

# Download firecracker
wget --no-clobber https://github.com/firecracker-microvm/firecracker/releases/download/${FC_VERSION}/firecracker-${FC_VERSION}-${ARCH}.tgz
tar -xvf firecracker-${FC_VERSION}-${ARCH}.tgz
cp release-${FC_VERSION}-${ARCH}/firecracker-${FC_VERSION}-${ARCH} /usr/local/bin/firecracker
rm -rf firecracker-${FC_VERSION}-${ARCH}.tgz release-${FC_VERSION}-${ARCH}/

# Download a linux kernel binary
wget --no-clobber https://s3.amazonaws.com/spec.ccfc.min/img/${ARCH}/ubuntu/kernel/vmlinux.bin

# Download a rootfs
wget --no-clobber https://s3.amazonaws.com/spec.ccfc.min/ci-artifacts/disks/${ARCH}/ubuntu-18.04.ext4

# Download the ssh key for the rootfs
wget --no-clobber https://s3.amazonaws.com/spec.ccfc.min/ci-artifacts/disks/${ARCH}/ubuntu-18.04.id_rsa

# Set user read permission on the ssh key
chmod 400 ./ubuntu-18.04.id_rsa

# Stop the firecracker process if it is already running
API_SOCKET="./firecracker.socket"
rm -f $API_SOCKET

# Run firecracker
killall firecracker || true
firecracker --api-sock "${API_SOCKET}" &

# set up the kernel boot args
TAP_DEV="fc-0-tap0"
MASK_LONG="255.255.255.252"
MASK_SHORT="/30"
FC_IP="169.254.0.21"
TAP_IP="169.254.0.22"

KERNEL_BOOT_ARGS="rw console=ttyS0 noapic reboot=k panic=1 pci=off nomodules random.trust_cpu=on ip=${FC_IP}::${TAP_IP}:${MASK_LONG}::eth0:off"

# set up a tap network interface for the Firecracker VM to user
ip link del "$TAP_DEV" 2> /dev/null || true
ip tuntap add "$TAP_DEV" mode tap
# sysctl -w net.ipv4.conf.${TAP_DEV}.proxy_arp=1 > /dev/null
# sysctl -w net.ipv6.conf.${TAP_DEV}.disable_ipv6=1 > /dev/null
ip addr add "${TAP_IP}${MASK_SHORT}" dev "$TAP_DEV"
ip link set "$TAP_DEV" up
FC_MAC="$(cat /sys/class/net/$TAP_DEV/address)"

# enable packet forwarding (for internet access)
DEVICE_NAME=$(ip route | grep default | awk '{print $5}')
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
sudo iptables -t nat -A POSTROUTING -o $DEVICE_NAME -j MASQUERADE
sudo iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i $TAP_DEV -o $DEVICE_NAME -j ACCEPT

# make a configuration file
cat <<EOF > fc-config.json
{
  "boot-source": {
    "kernel_image_path": "vmlinux.bin",
    "boot_args": "$KERNEL_BOOT_ARGS"
  },
  "drives": [
    {
      "drive_id": "rootfs",
      "path_on_host": "ubuntu-18.04.ext4",
      "is_root_device": true,
      "is_read_only": false
    }
  ],
  "network-interfaces": [
      {
          "iface_id": "$DEVICE_NAME",
          "guest_mac": "$FC_MAC",
          "host_dev_name": "$TAP_DEV"
      }
  ],
  "machine-config": {
    "vcpu_count": 2,
    "mem_size_mib": 1024
  }
}
EOF

# start firecracker
firecracker --no-api --config-file fc-config.json

# ssh -o StrictHostKeyChecking=false -i ubuntu-18.04.id_rsa root@169.254.0.21
