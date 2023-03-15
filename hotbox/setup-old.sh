#!/bin/bash -e

set -euo pipefail

# Install dependencies
tee -a /etc/security/limits.conf <<EOL
$USER soft nproc 16384
$USER hard nproc 16384
EOL

# Configure packet forwarding
sysctl -wq net.ipv4.conf.all.forwarding=1

# Avoid "neighbour: arp_cache: neighbor table overflow!"
sysctl -wq net.ipv4.neigh.default.gc_thresh1=1024
sysctl -wq net.ipv4.neigh.default.gc_thresh2=2048
sysctl -wq net.ipv4.neigh.default.gc_thresh3=4096

# Install and update packages
apt update -y
apt install iperf3 -y

# Update permissins
chmod 777 /dev/kvm

# Install Firecracker
FC_FILE_PATH=$HOME/firecracker
TMP_FOLDER='/tmp/tmpfc'
TMP_ARCHIVE='/tmp/tmpfcrelease.tgz'
wget 'https://github.com/firecracker-microvm/firecracker/releases/download/v1.3.1/firecracker-v1.3.1-aarch64.tgz' -O $TMP_ARCHIVE
mkdir -p $TMP_FOLDER
tar -xvf $TMP_ARCHIVE -C $TMP_FOLDER
cp $TMP_FOLDER/release-v1.3.1-aarch64/firecracker-v1.3.1-aarch64 $FC_FILE_PATH
rm -rf "$TMP_FOLDER"
rm "$TMP_ARCHIVE"

# Install rootfs
KERNEL_FILE_PATH=$HOME/vmlinux
wget -q "https://s3.amazonaws.com/spec.ccfc.min/ci-artifacts/kernels/aarch64/vmlinux-4.14.bin" -O $KERNEL_FILE_PATH
ROOTFS_FILE_PATH="$HOME/rootfs.ext4"
ROOTFS_KEY_PATH="$HOME/rootfs.id_rsa"
wget -q "https://s3.amazonaws.com/spec.ccfc.min/ci-artifacts/disks/aarch64/ubuntu-18.04.ext4" -O $ROOTFS_FILE_PATH
wget -q "https://s3.amazonaws.com/spec.ccfc.min/ci-artifacts/disks/aarch64/ubuntu-18.04.id_rsa" -O $ROOTFS_KEY_PATH
chmod 400 $ROOTFS_KEY_PATH

# Set up
provision_microvm() {
    # Setup TAP device that uses proxy ARP
    # VM_ID="${1}"
    VM_ID="0"
    TAP_DEV="fc-${VM_ID}-tap0"
    MASK_SHORT="/30"
    TAP_IP="$(printf '169.254.%s.%s' $(((4 * VM_ID + 2) / 256)) $(((4 * VM_ID + 2) % 256)))"

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

    API_SOCKET="$HOME/fc-socks/fc-sb${VM_ID}.socket"
    LOGFILE="$HOME/fc-logs/fc-${VM_ID}.log"

    rm -f $API_SOCKET
    $HOME/firecracker --api-sock $API_SOCKET &

    # create logfile
    touch "$LOGFILE"

    # set logfile
    curl -X PUT --unix-socket "${API_SOCKET}" \
        --data "{
            \"log_path\": \"${LOGFILE}\",
            \"level\": \"Debug\",
            \"show_level\": true,
            \"show_log_origin\": true
        }" \
        "http://localhost/logger"

    KERNEL_BOOT_ARGS="console=ttyS0 reboot=k panic=1 pci=off"
    ARCH=$(uname -m)

    if [ ${ARCH} = "aarch64" ]; then
        KERNEL_BOOT_ARGS="keep_bootcon ${KERNEL_BOOT_ARGS}"
    fi

    # Set boot source
    curl -X PUT --unix-socket "${API_SOCKET}" \
        --data "{
            \"kernel_image_path\": \"${KERNEL_FILE_PATH}\",
            \"boot_args\": \"${KERNEL_BOOT_ARGS}\"
        }" \
        "http://localhost/boot-source"

    # Set rootfs
    curl -X PUT --unix-socket "${API_SOCKET}" \
        --data "{
            \"drive_id\": \"rootfs\",
            \"path_on_host\": \"${ROOTFS_FILE_PATH}\",
            \"is_root_device\": true,
            \"is_read_only\": false
        }" \
        "http://localhost/drives/rootfs"

    # The IP address of a guest is derived from its MAC address with
    # `fcnet-setup.sh`, this has been pre-configured in the guest rootfs. It is
    # important that `TAP_IP` and `FC_MAC` match this.
    FC_MAC=$(ip addr show $TAP_DEV | grep link/ether | awk '{print $2}')

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
    sleep 0.015s

    # Start microVM
    curl -X PUT --unix-socket "${API_SOCKET}" \
        --data "{
            \"action_type\": \"InstanceStart\"
        }" \
        "http://localhost/actions"

    # API requests are handled asynchronously, it is important the microVM has been
    # started before we attempt to SSH into it.
    sleep 0.015s
}

provision_microvm


# mkdir -p "$HOME/fc-logs" "$HOME/fc-socks"
# upperlim="${2:-1}"
# parallel="${3:-1}"

# for ((i=0; i<100; i++)); do
#   s=$((i * upperlim / 100))
#   e=$(((i+1) * upperlim / 100))
#   for ((j=s; j<e; j++)); do
#     provision_microvm "$j"
#   done &
# done
