import os

os.environ["TZ"] = "UTC"

# TODO: ✅ create baremetal ec2 instance on aws
# TODO: provision the vm with firecracker, kernel, and rootfs – via userdata
# TODO: create taps for the vms - via userdata
# TODO: create network bridges for the vms (host to vm, vm to host,
#   vm to vm) – via userdata
# TODO: run healthchecks on the vms (iperf3, ping, etc, apps, etc) - command
# TODO: deploy apps to the vm - command
