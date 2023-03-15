#!/bin/sh

fdisk -l

mkdir /mnt
mount /dev/vdb /mnt

# ifconfig eth0 up && ip addr add dev eth0 169.254.0.21/24
# ip route add default via 169.254.0.21 && echo "nameserver 8.8.8.8" > /etc/resolv.conf
