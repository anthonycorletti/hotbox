Let's use hotbox to run your code in the cloud on a Firecracker MicroVM.

## Requirements

- Python 3.10: You can install Python 3.10 using [pyenv](https://github.com/pyenv/pyenv).
- An AWS Account. Sign up for free [here](https://aws.amazon.com/free/).
- [jq](https://stedolan.github.io/jq/)

Check that python is installed by running:

```bash
python --version
```

Log in to your AWS account by running:

```bash
aws configure
```

To make sure that you're logged in, run:

```bash
aws sts get-caller-identity
```

Check that jq is installed by running:

```bash
jq --version
```

## Install hotbox

```bash
pip install hotbox
```

## Write some code!

We have example code [here](https://github.com/anthonycorletti/hotbox/blob/main/examples/).

## Create an EC2 Instance using hotbox

We cover all the steps you need to set something up, if you already have an EC2 key-pair and security group, you can skip to the [Create the EC2 Instance](#create-the-ec2-instance) section.

### Create a key-pair and adjust the permissions

```bash
export REGION=us-east-1
aws ec2 create-key-pair --key-name hotbox-example-$REGION --region $REGION | jq -r '.KeyMaterial' > ~/hotbox-example-$REGION.pem
chmod 600 ~/hotbox-example-$REGION.pem
```

### Create a security group

```bash
SECURITY_GROUP_ID=$(aws ec2 create-security-group --group-name hotbox-example-all-traffic --description "All traffic allowed" --vpc-id $(aws ec2 describe-vpcs --region $REGION | jq -r '.Vpcs[] | select(.IsDefault) | .VpcId') --region $REGION | jq -r '.GroupId')
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --region $REGION --protocol all --port all --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --region $REGION --ip-permissions IpProtocol=-1,Ipv6Ranges='[{CidrIpv6=::/0}]'
aws ec2 authorize-security-group-egress --group-id $SECURITY_GROUP_ID --region $REGION --ip-permissions IpProtocol=-1,Ipv6Ranges='[{CidrIpv6=::/0}]'
```

### Create the EC2 Instance

```bash
hotbox create ec2 --region $REGION --key-name hotbox-example-$REGION --security-group-ids $SECURITY_GROUP_ID
```

### Confirm that hotbox is running on the EC2 Instance

This should print `ok`. It might take a few minutes for the EC2 Instance to start up.

```bash
curl -s $(hotbox get ec2 --region $REGION | jq -r '.Reservations[] | select(.Instances[] | .State.Name == "running") | .Instances[].PublicIpAddress'):8088/api/v0/healthcheck | jq -r .message
```

## Deploy your code!

Set your hotbox API URL as an environment variable:

```bash
export HOTBOX_API_URL="http://$(hotbox get ec2 --region $REGION | jq -r '.Reservations[] | select(.Instances[] | .State.Name == "running") | .Instances[].PublicIpAddress'):8088/api/v0"
```

Let's use our example go code. You can find the code [here](https://github.com/anthonycorletti/hotbox/blob/main/examples/go).

```bash
hotbox create app -n my-app -c examples/go
```

## Check that your code was deployed and is running

This example runs internally on the EC2 Instance, so we can check the status of the app on the EC2 Instance.

```bash
ssh -i ~/hotbox-example-$REGION.pem ubuntu@$(hotbox get ec2 --region $REGION | jq -r '.Reservations[] | select(.Instances[] | .State.Name == "running") | .Instances[].PublicIpAddress')
```

Now that you're on the instance, run:

```bash
curl -s http://192.168.0.1:8080/hotbox
```

This should print `Hi there, hotbox!`.

`192.168.0.1` is the IP address of the Firecracker MicroVM. Hotbox automatically set that up for you.

## Cleanup!

### Delete the EC2 Instance

```bash
hotbox delete ec2 $(hotbox get ec2 --region $REGION | jq -r '.Reservations[0].Instances[0] | .InstanceId') --region $REGION
```

### Delete the security group

```bash
aws ec2 delete-security-group --group-id $SECURITY_GROUP_ID --region $REGION
```

### Delete the key-pair

```bash
aws ec2 delete-key-pair --key-name hotbox-example-$REGION --region $REGION
```
