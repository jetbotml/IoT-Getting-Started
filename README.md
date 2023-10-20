# AWS IoT using a Raspberry Pi

## Prep AWS: Create AWS S3 bucket, IAM role and (optional) SSM activation

1. Create S3 bucket from the Amazon S3 Service
    - Select Create bucket
    - Bucket name: (must be unique - see rules for bucket naming) someting like your initials + date + iotpi. (all lowercase, numbers, no spaces)
    - keep defaults - select Create bucket button
1. Create Role with S3 download permissions from IAM
    - Select User
    - Select Create User. User name: PiS3Download, then select Next
    - Add Access Key: Command Line Interface (CLI)
    - Download user access key and secret
1. Create SSM activation from AWS Systems Manager/Node Management/Hybird Activations
    - Select Create activation
    - Enter Activation Date (needs to be a few days in advance)
    - Select Create activation button
    - Copy the "activation-code" -id "activation-id" for use later


## Prep Raspberry Pi
1. Flash latest OS image
    - Use Raspberry Pi Imager (https://www.raspberrypi.com/software/)
    - Select Raspberry Pi OS (64 bit)
1. Boot the Pi and follow instructions
1. Install AWS CLI
    - sudo apt install awscli -y
    - run aws configure - input the access key and secret
    - test run aws s3 ls
1. Install SSM Agent
    - sudo curl https://s3.us-east-2.amazonaws.com/amazon-ssm-us-east-2/latest/debian_arm64/amazon-ssm-agent.deb -o amazon-ssm-agent.deb
    - sudo dpkg -i amazon-ssm-agent.deb
    - sudo service amazon-ssm-agent stop
    - sudo amazon-ssm-agent -register -code "activation-code" -id "activation-id" -region "us-east-1"
    - sudo service amazon-ssm-agent start

## Connect a Raspberry Pi to AWS IoT Core
1. Select Connect a device button
1. Test a ping connection from your pi to your AWS IoT (click next)
1. Enter a Thing name (click next)
1. Select Linix for device OS and choose your SDK. (recomend Python) (click next)
1. Download connection kit
1. Copy connection kit to your S3 bucket
1. From your pi command line; download, unpack, setup and start the connection kit
    - aws s3 cp s3//bucketnameXX/connection_device_package.zip ./
    - follow instructions and run the kit

## Send Pi system data to AWS IoT
1. make a copy of the start.sh
    - cp start.sh mystart.sh
1. add the following to the nystart.sh before the # run pub/sub sample app using certificates downloaded in package
   ```python
    if [ ! -d ./utils ]; then
      printf "\nCloning the util folder...\n"
      cp -r ~/aws-iot-device-sdk-python-v2/samples/utils ~/
    fi
    ```
1. Modify the last line in the mystart.sh remove the path and rename the file 
   - from
   - python3 aws-iot-device-sdk-python-v2/samples/pubsub.py --endpoint......
   - to
   - python3 mypubsub.py --endpoint......
  
1. Copy updated file to mystart.sh location
