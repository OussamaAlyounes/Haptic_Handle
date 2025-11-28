import serial
import time

if __name__=="__main__":
    
    # function to send data to Arduino
    ser = serial.Serial("COM5", 9600)
    angle = 90
    ser.write(f"{angle}".encode())

    i = 0
    angle = range(0,170,15)
    time_start = time.time()
    
    while i<len(angle):
        if time.time() - time_start >3:
            # x=1
            ser.write(f"{angle[i]}".encode())
            i+=1
            time_start = time.time()
        if ser.in_waiting>0:
            print(ser.readline().decode(errors='igonre'))
            # received = True
        # ser.close()

    ser.close()
    print("finished")
