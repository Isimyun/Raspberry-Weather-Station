import RPi.GPIO as GPIO
import time
import Project_Testing as DHT
import smbus
import time
from ctypes import c_short
from time import sleep
from pyrebase import pyrebase
import base64
from datetime import datetime


DHTPin = 11     #define the pin of DHT11
DEVICE = 0x77 # Default device I2C address
GPIO.setwarnings(False)
 
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

config = {
  "apiKey": "AIzaSyBML8cxQ8MJN0Zvz4s_n-de8heivfPOqfw",
  "authDomain": "group-project-4b008.firebaseapp.com",
  "databaseURL": "https://group-project-4b008-default-rtdb.firebaseio.com/",
  "storageBucket": "group-project-4b008.appspot.com"
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password("immanuelsy2112@gmail.com", "123456")
db = firebase.database()



def convertToString(data):
  # Simple function to convert binary data into
  # a string
  return str((data[1] + (256 * data[0])) / 1.2)

def getShort(data, index):
  # return two bytes from data as a signed 16-bit value
  return c_short((data[index] << 8) + data[index + 1]).value

def getUshort(data, index):
  # return two bytes from data as an unsigned 16-bit value
  return (data[index] << 8) + data[index + 1]

def readBmp180Id(addr=DEVICE):
  # Chip ID Register Address
  REG_ID     = 0xD0
  (chip_id, chip_version) = bus.read_i2c_block_data(addr, REG_ID, 2)
  return (chip_id, chip_version)
  
def readBmp180(addr=DEVICE):
  # Register Addresses
  REG_CALIB  = 0xAA
  REG_MEAS   = 0xF4
  REG_MSB    = 0xF6
  REG_LSB    = 0xF7
  # Control Register Address
  CRV_TEMP   = 0x2E
  CRV_PRES   = 0x34 
  # Oversample setting
  OVERSAMPLE = 3    # 0 - 3
  
  # Read calibration data
  # Read calibration data from EEPROM
  cal = bus.read_i2c_block_data(addr, REG_CALIB, 22)
  
  # Convert byte data to word values
  AC1 = getShort(cal, 0)
  AC2 = getShort(cal, 2)
  AC3 = getShort(cal, 4)
  AC4 = getUshort(cal, 6)
  AC5 = getUshort(cal, 8)
  AC6 = getUshort(cal, 10)
  B1  = getShort(cal, 12)
  B2  = getShort(cal, 14)
  MB  = getShort(cal, 16)
  MC  = getShort(cal, 18)
  MD  = getShort(cal, 20)

  # Read temperature
  bus.write_byte_data(addr, REG_MEAS, CRV_TEMP)
  time.sleep(0.005)
  (msb, lsb) = bus.read_i2c_block_data(addr, REG_MSB, 2)
  UT = (msb << 8) + lsb

  # Read pressure
  bus.write_byte_data(addr, REG_MEAS, CRV_PRES + (OVERSAMPLE << 6))
  time.sleep(0.04)
  (msb, lsb, xsb) = bus.read_i2c_block_data(addr, REG_MSB, 3)
  UP = ((msb << 16) + (lsb << 8) + xsb) >> (8 - OVERSAMPLE)

  # Refine temperature
  X1 = ((UT - AC6) * AC5) >> 15
  X2 = (MC << 11) / (X1 + MD)
  B5 = X1 + X2
  temperature = int(B5 + 8) >> 4

  # Refine pressure
  B6  = B5 - 4000
  B62 = int(B6 * B6) >> 12
  X1  = (B2 * B62) >> 11
  X2  = int(AC2 * B6) >> 11
  X3  = X1 + X2
  B3  = (((AC1 * 4 + X3) << OVERSAMPLE) + 2) >> 2

  X1 = int(AC3 * B6) >> 13
  X2 = (B1 * B62) >> 16
  X3 = ((X1 + X2) + 2) >> 2
  B4 = (AC4 * (X3 + 32768)) >> 15
  B7 = (UP - B3) * (50000 >> OVERSAMPLE)

  P = (B7 * 2) / B4

  X1 = (int(P) >> 8) * (int(P) >> 8)
  X1 = (X1 * 3038) >> 16
  X2 = int(-7357 * P) >> 16
  pressure = int(P + ((X1 + X2 + 3791) >> 4))

  return pressure/100.0

def loop():
    dht = DHT.DHT(DHTPin)   #create a DHT class object
    counts = 0 # Measurement counts
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M")
    
    for j in range(10):
        counts += 1
        print("Measurement counts: ", counts)
        pressure=readBmp180()
        for i in range(0,15):            
            chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
                print("DHT11,OK!")
                break
            time.sleep(0.1)        
        print("Humidity : %.2f"%(dht.humidity))
        print("Temperature: %.2f"%(dht.temperature))
        print("Pressure: %.2f mbar\n" %(pressure))
        data = {
                "timestamp":current_time,
                "humidity":dht.humidity,
                "temperature":dht.temperature,
                "pressure":pressure
                }
        results = db.child("measurement").push(data, user['idToken'])        
        time.sleep(2)
        
        
        
if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
        exit()
    print("Program Finished!")


