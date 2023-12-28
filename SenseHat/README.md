## Sense Hat 

### Steps - adding sense-hat data to publish to AWS and subscribing to message to process on the pi


<img src='https://github.com/jetbotml/IoT-Getting-Started/blob/main/SenseHat/SenseHat.png' width="40%" height="40%">

Sense HAT - https://www.raspberrypi.com/products/sense-hat/

Product Brief - https://datasheets.raspberrypi.com/sense-hat/sense-hat-product-brief.pdf

Reference: https://pythonhosted.org/sense-hat/


### Install
Install the Sense HAT software by opening a Terminal window and entering the following commands (while connected to the Internet):

- **sudo apt-get update**
- **sudo apt-get install sense-hat**
- **sudo reboot**

### publish Sense HAT data 
1. Use updated python file https://github.com/jetbotml/IoT-Getting-Started/blob/main/SenseHat/myshpubsub.py
2. Change IoT Policy to https://github.com/jetbotml/IoT-Getting-Started/blob/main/SenseHat/policy.txt

example data

  <img src='https://github.com/jetbotml/IoT-Getting-Started/blob/main/SenseHat/IoTDataExample2.png' width="30%" height="30%">

3. Subscribe to message to process on the pi
  - Use AWS IoT to publish message and change the color on the sense-hat leds.
  - The pi is looking for red, green and/or blue in the message.

