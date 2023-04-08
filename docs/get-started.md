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

```
aws ec2 create-key-pair --key-name hotbox-example --region us-east-1 | jq -r '.KeyMaterial' > ~/hotbox-example.pem
chmod 600 ~/hotbox-example.pem
```

### Create a security group

```bash
SECURITY_GROUP_ID=$(aws ec2 create-security-group --group-name hotbox-example --description "Security group with all traffic allowed" --vpc-id $(aws ec2 describe-vpcs | jq -r '.Vpcs[] | select(.IsDefault) | .VpcId') --region us-east-1 | jq -r '.GroupId')
```

### Add a rule to the security group

```bash
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol all --port all --cidr 0.0.0.0/0 --region us-east-1
```

### Create the EC2 Instance

```bash
hotbox create ec2 --region us-east-1 --key-name hotbox-example --security-group-ids $SECURITY_GROUP_ID
```

### Confirm that hotbox is running on the EC2 Instance

This should print `ok`. It might take a few minutes for the EC2 Instance to start up.

```bash
curl -s $(hotbox get ec2 --region us-east-1 | jq -r '.Reservations[] | select(.Instances[] | .State.Name == "running") | .Instances[].PublicDnsName')/api/v0/healthcheck | jq -r .message
```

## Deploy your code!

Set your hotbox API URL as an environment variable:

```bash
export HOTBOX_API_URL="http://$(hotbox get ec2 --region us-east-1 | jq -r '.Reservations[] | select(.Instances[] | .State.Name == "running") | .Instances[].PublicDnsName')/api/v0"
```

Let's use our example go code. You can find the code [here](https://github.com/anthonycorletti/hotbox/blob/main/examples/go).

```bash
hotbox create app -c examples/go
```

## Check that your code was deployed and is running

This example runs internally on the EC2 Instance, so we can check the status of the app by sshing into the EC2 Instance and curling to the app.

```bash
ssh -i ~/hotbox-example.pem ubuntu@$(hotbox get ec2 --region us-east-1 | jq -r '.Reservations[] | select(.Instances[] | .State.Name == "running") | .Instances[].PublicDnsName')
```

Now that you're on the instance, run:

```bash
curl -s localhost:8080/hotbox | jq -r .message
```

This should print `Hi there, hotbox!`.

## Cleanup!

### Delete the EC2 Instance

```bash
hotbox delete ec2 $(hotbox get ec2 --region us-east-1 | jq -r '.Reservations[0].Instances[0] | .InstanceId') --region us-east-1
```

### Delete the security group

```bash
aws ec2 delete-security-group --group-id $SECURITY_GROUP_ID --region us-east-1
```

### Delete the key-pair

```bash
aws ec2 delete-key-pair --key-name hotbox-example --region us-east-1
```
