#!/usr/bin/env python

import sys
import logging
import serial
import argparse
import time
import pandas as ps
from datetime import datetime

FORMAT = '%(levelname)-5s %(message)s'

logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG

data = []


class PS3005D(object):

    device = None

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='PS3005D logger',
            usage='''ps3005d <port> <command> [<args>]

The available commands are:
   id       Get power supply id
   on       Turn on
   off      Turn off  
   voltage
''')

        parser.add_argument('port',type=str,help='PS3005D serial port e.g. /dev/tty.usbmodem1411')
        parser.add_argument('command', help='Subcommand to run')
        parser.add_argument('--baud',dest='baud',type=int,default=9600)
        args = parser.parse_args(sys.argv[1:3])
        
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)

        try:
            self.device = serial.Serial(args.port, args.baud, timeout=1)
        except:
            logger.error('Could not connect to device on {0}'.format(args.port))
            exit(2)

        getattr(self, args.command)()

    def _send(self,msg):
        # msg += '\r\n'
        # logger.debug('Sending: {0}'.format(msg))
        self.device.write(msg)

    def _receive(self,timeout=2000):
        end_time = time.time()+(timeout/1000)
        payload=''
        while(end_time-time.time() > 0):
            c = self.device.readline()
            if c:
                payload+=c
                break

        return payload


    def id(self):
        """ Get the power supply id """
        parser = argparse.ArgumentParser(
            description=self.id.__doc__)
        args = parser.parse_args(sys.argv[3:])
        self._send('*IDN?')
        payload=self._receive()
        return payload

    def on(self):
        """ Turn on the power supply """

        parser = argparse.ArgumentParser(
            description=self.on.__doc__)
        args = parser.parse_args(sys.argv[3:])
        self._send('OUT1')
        logger.info('Power ON')

    def off(self):
        """ Turn off the power supply """

        parser = argparse.ArgumentParser(
            description=self.off.__doc__)
        args = parser.parse_args(sys.argv[3:])
        self._send('OUT0')    
        logger.info('Power OFF')

    def voltage(self):
        """ TSet power supply voltage """

        parser = argparse.ArgumentParser(
            description=self.voltage.__doc__)
        parser.add_argument('voltage',type=float,help='voltage to set')
        args = parser.parse_args(sys.argv[3:])
        self._send('VSET1:{0}'.format(args.voltage))
        logger.info('Voltage set to {0}V'.format(args.voltage))

    def current(self):
        """ Set power supply current """

        parser = argparse.ArgumentParser(
            description=self.current.__doc__)
        parser.add_argument('current',type=float,help='current to set')
        args = parser.parse_args(sys.argv[3:])
        self._send('ISET1:{0}'.format(args.current))
        logger.info('Current set to {0}V'.format(args.current))

    def enable_ovp(self):
        """ Enable over-voltage protection """
        parser = argparse.ArgumentParser(
            description=self.enable_ovp.__doc__)
        args = parser.parse_args(sys.argv[3:])
        self._send('OVP1')
        logger.info('Enabled OVP')

    def disable_ovp(self):
        """ Disable over-voltage protection """
        parser = argparse.ArgumentParser(
            description=self.disable_ovp.__doc__)
        args = parser.parse_args(sys.argv[3:])
        self._send('OVP0')
        logger.info('Disabled OVP')


    def enable_ocp(self):
        """ Enable over-voltage protection """
        parser = argparse.ArgumentParser(
            description=self.enable_ocp.__doc_)
        args = parser.parse_args(sys.argv[3:])
        self._send('OCP1')
        logger.info('Enabled OCP')


    def disable_ocp(self):
        """ Disable over-current protection """
        parser = argparse.ArgumentParser(
            description=self.disable_ocp.__doc__)
        args = parser.parse_args(sys.argv[3:])
        self._send('OCP0')
        logger.info('Disabled OCP')


    def load_voltage(self):
        """ Get the load voltage """
        parser = argparse.ArgumentParser(
            description=self.load_voltage.__doc__)
        args = parser.parse_args(sys.argv[3:])
        parser.add_argument('--silent',dest='silent',type=bool,action='store_true',default=False,help="Don't print result")
        self._send('VOUT1?')
        payload=self._receive()
        if not args.silent:
            print(payload)
        return payload

    def load_current(self):
        """ Get the load current """ 
        parser = argparse.ArgumentParser(
            description=self.load_current.__doc__)
        parser.add_argument('--silent',dest='silent',type=bool,action='store_true',default=False,help="Don't print result")

        args = parser.parse_args(sys.argv[3:])
        self._send('IOUT1?')
        payload=self._receive()
        if not args.silent:
            print(payload)
        return payload

    def log(self):
        """ Log load voltage and current to a csv """
        parser = argparse.ArgumentParser(
            description=self.log.__doc__)
        parser.add_argument('voltage',type=float,help='voltage to set')
        parser.add_argument('current',type=float,help='current to set')
        parser.add_argument('--freq',dest='freq',type=int,default=1000,help='logging frequency in ms, default 1000ms')
        parser.add_argument('--log',dest='log',type=str,default='log.csv',help='log csv filename, default log.csv')
        args = parser.parse_args(sys.argv[3:])
        
        logger.info('Logging {0}V, {1}A every {2}ms'.format(args.voltage,args.current,args.freq))

        self.voltage(args.voltage)
        time.sleep(0.2)
        self.current(args.current)
        time.sleep(0.2)
        self.enable_ovp()
        time.sleep(0.2)
        self.enable_ocp()
        time.sleep(0.2)
        self.on()
        time.sleep(0.2)
        timestamps = []
        voltages = []
        currents = []
        try:
            while True:
                v = self.load_voltage()
                i = self.load_current()
                timestamp = datetime.now()
                timestamps.append(timestamp)
                voltages.append(v)
                currents.append(i)
                time.sleep(args.freq/1000)
        except KeyboardInterrupt:
            self.off()
       
        df = ps.DataFrame(data={'voltage':voltages,'current':currents},index=timestamps)

        df.to_csv(args.log,index_label='timestamp')
        logger.info('Saved {0} records to {1}'.format(len(df),args.log))

        return df

def main():

    PS3005D()



if __name__ == '__main__':
    main()
