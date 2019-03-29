
from flask import Flask, render_template, Response, stream_with_context, copy_current_request_context,redirect,url_for 
from flask_socketio import SocketIO
from time import sleep
from threading import Thread, Event
import random
import serial
from tkinter import *
#app = Flask(__name__)
#app.config['SECRET_KEY'] = 'secret!'
#socketio = SocketIO(app)

import RPi.GPIO as GPIO   
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
red=4
green=3
buzz=2
pir=26
metal=19
motor1a=12              #Two motors
motor1b=16
motor2a=20
motor2b=21
GPIO.setup(buzz,GPIO.OUT)
GPIO.setup(green,GPIO.OUT)
GPIO.setup(red,GPIO.OUT)
GPIO.setup(pir,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(metal,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(motor1a,GPIO.OUT)
GPIO.setup(motor1b,GPIO.OUT)
GPIO.setup(motor2a,GPIO.OUT)
GPIO.setup(motor2b,GPIO.OUT)
i=1
a=0
gps_port='/dev/ttyUSB0'
ser = serial.Serial(gps_port, baudrate = 9600, timeout = 0.5)
def GPS():
    try:
        data = ser.readline()
    except:
        print('loading')
	#wait for the serial port to churn out data

    if data[0:6] == '$GPGGA': # the long and lat data are always contained in the GPGGA string of the NMEA data

        msg = pynmea2.parse(data)

	#parse the latitude and print
        latval = msg.latitude
        longval = msg.longitude
        time.sleep(0.5)

        return [latval,longval]

def pir_status():
    if GPIO.input(pir)==True:
        status="Intruder alert"
        GPIO.output(red,GPIO.HIGH)
        GPIO.output(green,GPIO.LOW)
        GPIO.output(buzz,GPIO.HIGH)
        time.sleep(5)
    else:
        status="PIR Normal"
        GPIO.output(red,GPIO.LOW)
        GPIO.output(green,GPIO.HIGH)
        GPIO.output(buzz,GPIO.LOW)
    return status

def detector():
    if GPIO.input(metal)==False:
        status="Landmine is Detected"
        GPIO.output(red,GPIO.HIGH)
        GPIO.output(green,GPIO.LOW)
        GPIO.output(buzz,GPIO.HIGH)
        time.sleep(5)
    else:
        status="No Landmine"
        GPIO.output(red,GPIO.LOW)
        GPIO.output(green,GPIO.HIGH)
        GPIO.output(buzz,GPIO.LOW)
    return status

coords=None   
def calculate():
    pirs=pir_status()
    mine=detector()
    for i in range(5):
        gps=GPS()
        if gps!=None and gps!=[0.0,0.0]:
            latitude=gps[0]
        else:
            latitude='Not available'
            longitude='Not available'
    #pirs="hi vinod"
    #mine="NOT Detecteed"
    #latitude='Not available'
    #longitude='Not available'
        
    list=[pirs,mine,latitude,longitude]
                  
        
        
    #list=[0,1,2,3,4]
    return list



app = Flask(__name__,static_url_path='/static')
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

socketio = SocketIO(app)

thread = Thread()
thread_stop_event = Event()

class CountThread(Thread):
    def __init__(self):
        self.delay = 2
        super(CountThread, self).__init__()

    def ran(self):
        root = Tk()
        root.geometry('250x80+30+20')

        mainframe = Frame(root)
        mainframe.grid(column=1000, row=1000, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        best = StringVar()
        best.set('start')
        x1 = 12
        Label(mainframe,textvariable=best,bg='#321000',fg='#000fff000',font=("Helvetica",x1)).grid(column=1,row=1)
        while True:
            temp=calculate()
            print(temp)
            best.set('Pir Status:%s\n Mine Status:%s\n Latitude:%s\nLongitude:%s' % (temp[0],temp[1],temp[2],temp[3]))
            mainframe.update()
        root.mainloop()

    def run(self):
        self.ran()

@app.route('/')
def index():
        return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = CountThread()
        thread.start()

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')



@app.route("/move_forward")
def move_forward():                      #motor forward condition
    data1="FORWARD"
    GPIO.output(motor1a,GPIO.HIGH)
    GPIO.output(motor1b,GPIO.LOW)
    GPIO.output(motor2a,GPIO.LOW)
    GPIO.output(motor2b,GPIO.HIGH)#Moving forward code
    return 'true'

@app.route("/move_reverse")
def move_reverse():                      #motor reverse condition
    data1="BACK"
    GPIO.output(motor1a,GPIO.LOW)
    GPIO.output(motor1b,GPIO.HIGH)
    GPIO.output(motor2a,GPIO.HIGH)
    GPIO.output(motor2b,GPIO.LOW)
    return 'true'

@app.route("/stop/")
def stop():                         #motor stop condition
    data1="STOP"
    GPIO.output(motor1a,GPIO.LOW)
    GPIO.output(motor1b,GPIO.LOW)
    GPIO.output(motor2a,GPIO.LOW)
    GPIO.output(motor2b,GPIO.LOW)
    return 'true'

@app.route("/move_right")
def move_right():                        #motor right condition
    data1="RIGHT"
    GPIO.output(motor1a,GPIO.HIGH)
    GPIO.output(motor1b,GPIO.LOW)
    GPIO.output(motor2a,GPIO.HIGH)
    GPIO.output(motor2b,GPIO.LOW)
    return 'true'


@app.route("/move_left")
def move_left():                        #motor left condition 
        data1="LEFT"
        GPIO.output(motor1a,GPIO.LOW)
        GPIO.output(motor1b,GPIO.HIGH)
        GPIO.output(motor2a,GPIO.LOW)
        GPIO.output(motor2b,GPIO.HIGH)
        return 'true'


if __name__ == '__main__':
    socketio.run(app)
    app.run(host='0.0.0.0', debug=True)

   
