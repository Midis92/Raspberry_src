import os
import asyncio
import json
import time
import datetime
import re, uuid
import socket
import base64
from gpiozero import LED
from azure.iot.device.aio import IoTHubDeviceClient
red = LED(18)
def sensor():
 for i in os.listdir('/sys/bus/w1/devices'):
    if i != 'w1_bus_master1':
        ds18b20 = i
    return ds18b20
def is_cnx_active():
    hostname = "google.com"
    response = os.system("ping -c 1 " + hostname)
    if response == 0:
      return True
    else:
      return False
def machineinfo():
    h_name = socket.gethostname()
    IP_addres = socket.gethostbyname(h_name)
    print("Host Name is:" + h_name)
    print("Computer IP Address is:" + IP_addres)
    print("MAC address: ", end="")
    print(':'.join(re.findall('..', '%012x' %uuid.getnode())))
    print("Tarkistetaan internet yhteys...")
    
    while True:
     if is_cnx_active() is True:
        print("Yhdistetty!")
        break
     else:
        print("Reconnecting...")
        time.sleep(2)
        pass
    

def read(ds18b20):
    location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave'
    tfile = open(location)
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    celcius = temperature / 1000
    return celcius

class Body:
  def __init__(self, time, temp):
    self.time = time
    self.temp = temp
class Sysprop:
    def __init__(self, cont, cenc):
        self.cont = cont
        self.cenc = cenc
            

async def loop(ds18b20):
    while True:
        try:
            if read(ds18b20) is not None:
                dt = datetime.datetime.now()
                #file1 = open(r"/home/kayttaja/Public/Temps.txt", "a")
                body = Body(dt.strftime("%c"), "%0.3f" % read(ds18b20))
                #msg = "Time: " + dt.strftime("%c") + ", Temperature:" + "%0.3f" % read(ds18b20)
                #file1.write(msg + "\n")
                #file1.close()
                red.on()
                conn_str = "<connection string would be here.>"
                device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
                print("Sending message...")
                json_message = {
                    "Timestamp": body.time,
                    "Temperature": body.temp
                }
                utf8_message = json.dumps(json_message).encode("utf-8")
                await device_client.connect()
                await device_client.send_message(utf8_message)
                await device_client.shutdown()
                print("Message successfully sent!")
                red.off()
                time.sleep(60)
        except Exception as e:
            print(f"Error sending message: {e}")
            await asyncio.sleep(60)
            continue


if __name__ == "__main__":
    try:
        machineinfo()
        serialNum = sensor()
        asyncio.run(loop(serialNum))
        
    except KeyboardInterrupt:
        print("Operation stopped!")
    finally:
        i = input("\nDo you want to restart the program? [y/n] > ")
        i='y'
        if i == 'y':
            os.system('python "/home/kayttaja/Desktop/Testing_HUB.py"')
        else:
            print("Operations stopped.")
        
