import time
import serial
import os

# Use python 3
# Serial AT Commands Handbook: http://simcom.ee/documents/SIM808/SIM800%20Series_AT%20Command%20Manual_V1.09.pdf

# Created by Calder, copyright 2016!
# test by ming2

# Logs instr to file
def log(instr):
    with open('log.txt', 'a') as l:
        l.write(instr)
    l.close()

# Logs instr to file is global variable mode != 1
def fona_print(instr):
    if mode == 1:
        print(instr)
    else:
        print(instr)
        log(instr.rstrip() + '\n')

# Sends an SMS using the Fona
def fona_message(number, message):
    fona_write('AT+CMGF=1')
    a = fona_read('AT+CMGF SET')
    fona_print(a)
    fona_write('AT+CMGS="' + number + '"')
    a = fona_read('AT+CMGS SET')
    fona_print(a)
    fona_write(message + chr(26))

# Main parsing for commandlists
def fona_command(commandlist):
    if listcheck(commandlist):
        for command in commandlist:

            #Skips "commented" lines
            if command.find("#") == 0:
                last_command = command

            #Handles when you want to check expected returns and exits if the expect fails
            elif command.find("expect:") != -1:
                recieve = command[command.find(':') + 1:]
                if last_out.find(recieve.rstrip()):
                    fona_print("Expect Passed")
                    last_command = command
                else:
                    fona_print("Unexpected return to previous command: " + last_command.rstrip()) + "\n" + last_out
                    return False

            #Handles when a message needs to be sent
            elif command.find("message:") != -1:
                nummsg = command[command.find(':') + 1:] 
                number = nummsg[:nummsg.find(':')]
                message =  nummsg[nummsg.find(':') + 1:]
                fona_message(number, message)
                last_out = fona_read('Message Sent')
                fona_print(last_out)
                last_command = command

            #Handles message data sent to FONA (excludes data sent using message:)
            elif command.find("data:") != -1:
                message = command[command.find(':') + 1:]
                fona_write(message + chr(26))
                last_out = fona_read('Data')
                fona_print(last_out)
                last_command = command

            #Handles wait commands to pause execution and allow time for the Fona to respond
            elif command.find("wait:") != -1:
                wait = command[command.find(':') + 1:]
                time.sleep(float(wait.rstrip()))
                last_command = command

            #Otherwise pass the AT command as a raw command
            else:
                fona_print(command.rstrip())
                fona_write(command)
                last_out = fona_read(command)
                fona_print(last_out)
                last_command = command

                #If an error is returned 
                if last_out.find('ERROR') != -1:
                    return False
        return True

# Handles error messages 
def fona_error(instr, error):
    return 'ERROR: Fona responded with: \n' + error.rstrip() + ' \n To command: ' + instr.rstrip()

# Reads messages and returns strings to be printed by fona_print
def fona_read(instr):
    out = ''
    time.sleep(2)
    #Read every byte in the file
    while ser.inWaiting() > 0:
        tmp = ser.read(1)
        tmp = tmp.decode("utf8")
        if tmp != '':
            out += tmp

    #Handles extraneous circumstances
    if out.find('ERROR') != -1:
        return fona_error(instr, out)    
    elif out != '':
        return out
    else:
        return "No Message Received: Ensure the device is connected and powered up"

# Writes bytes to fona to command
def fona_write(instr):
    i = strcheck(instr)
    if (i == 0):
        out = instr + '\r\n'
        out = bytes(out.encode("utf8"))
    elif (i == 1):
        out = instr
    else:
        return 'Type error in fona_write'
    ser.write(out)
    return 

# Checks to see if the input is a string or bytes
def strcheck(instr):
    if (type(instr) == str):
        return 0
    elif (type(instr) == bytes):
        return 1
    else: 
        return 2

# Check to see if input is a list
def listcheck(commandlist):
    if (type(commandlist) == list):
        return True
    fona_print("Invalid commandlist")
    return False

# Loads a text file of commands that can be read by the parsing engine
def loadcommandfile(path):
    try:
        with open(path, 'r') as f:
            commands = f.readlines()
        f.close()
        return commands
    except IOError:
        fona_print('Error reading file')
        return

# Setup serial connection:
#TODO: Auto detect dev port
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=115200,
    #parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

# Instructions
print('Enter your commands below.\r\nInsert "exit" to leave the application.\r\nInsert "read:filename" to execute a text file command.\r\nInsert "loop:filename" to repeat the same text file command')

global mode 
mode = 0

if __name__ == '__main__':
    uinput='AT'
    while 1 :
        # get keyboard input
        uinput = input('>> ')
            # Python 3 users
            # input = input(">> ")
        if (uinput == 'exit'):
            ser.close()
            exit()

        # Reads a command file once 
        elif (uinput.find('read:') != -1):
            path = uinput[uinput.find(':') + 1:]
            commandlist = loadcommandfile(path)
            if commandlist != None:
                fona_command(commandlist)

        # Repeats a standard command to the fona for example execute the lines of a file. 
        elif (uinput.find('loop:') != -1):
            path = uinput[uinput.find(':') + 1:]
            commandlist = loadcommandfile(path)
            if commandlist != None:
                while fona_command(commandlist):
                    1
            #TODO: Alert OS to reset fona connection and verify fona is working with read:check.txt
            #TODO: Reset path periodically and sleep between calls to allow file rewrites with new telemetry

        # Direct messages the fona to perform an AT command
        elif (uinput.find('message:') != -1):
            nummsg = uinput[uinput.find(':') + 1:] 
            number = nummsg[:nummsg.find(':')]
            message =  nummsg[nummsg.find(':') + 1:]
            fona_message(number, message)
            a = fona_read('Message Sent')
            fona_print(a)

        else:
            fona_write(uinput)
            out = fona_read(uinput)
            fona_print(out)
