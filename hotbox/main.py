import os

os.environ["TZ"] = "UTC"

# TODO: ✅ create baremetal ec2 instance on aws – command
# TODO: ✅ provision the vm with firecracker, kernel, and rootfs, taps and bridges – via userdata which comes from the spec
# TODO: ✅ run healthchecks on the new vms (ping outside and inside)
# TODO: deploy apps on microvms to the ec2 instance (cli.create.app)
# TODO: mount larger directories for each app (building root fs)
# TODO: implement microvm to microvm communication (Same host microvm-to-microvm, different host microvm-to-microvm, internet to microvm, microvm to internet)
# TODO: demo that simulates something like the firecracker demo
# TODO: implement jailer
