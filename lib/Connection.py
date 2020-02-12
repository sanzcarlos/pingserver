#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import socket
import os
import configparser
import ipaddress
import time

from enum import Enum

class ResponseDetail(Enum):
    TCP = 'TCP'
    ICMP = 'ICMP'
    INVALID_IP = 'INVALID_IP'
    ERROR = 'ERROR'

class ResponseStatus(Enum):
    OK = 'OK'
    KO = 'KO'
    UNK = 'UNK'

config = configparser.ConfigParser()
config.read('conf/pingsrv.conf')
TIMEOUT = config.get('Parametros', 'timeout')
TEST_PORT = config.get('Parametros', 'test_port').split(',')
PING_COMMAND = config.get('Parametros', 'ping_command')
PING_COUNT = config.get('Parametros', 'ping_count')

class Connection(object):

    def __init__(self, ipaddress, infoLogger, timeout=TIMEOUT, test_port=TEST_PORT, ping_command=PING_COMMAND, ping_count=PING_COUNT):
        self.ipaddress = ipaddress
        self.Logger = infoLogger
        self.family = 2
        self.timeout = float(timeout) # segundos
        self.test_port = test_port
        self.ping_command = ping_command
        self.ping_count = ping_count
        if ipaddress.version == 6:
            self.family = 10
            self.ping_command += '6'
        self.Logger.debug ('Puertos a Comprobar: %s' % (self.test_port))

    def run(self):
        error = 0
        t_all = time.time()
        for i in range(len(self.test_port)):
            t_start = time.time()
            try:                
                with socket.socket(self.family, socket.SOCK_STREAM) as s:
                    s.settimeout(self.timeout)
                    s.connect((self.ipaddress.compressed, int(self.test_port[i])))
                self.Logger.debug ('Status 0: %s | IP: %s | Port: %s | Detail: %s | Time: %s' % (ResponseStatus.OK.value,self.ipaddress.compressed,self.test_port[i],ResponseDetail.TCP.value,(time.time() - t_start)))
                return {'Status': ResponseStatus.OK.value, 'Detail': ResponseDetail.TCP.value, 'Port': self.test_port[i], 'Time':(time.time()-t_all)}
            except ConnectionError:
                self.Logger.debug ('Status 1: %s | IP: %s | Port: %s | Detail: %s | Time: %s' % (ResponseStatus.OK.value,self.ipaddress.compressed,self.test_port[i],ResponseDetail.TCP.value,(time.time() - t_start)))
                return {'Status': ResponseStatus.OK.value, 'Detail': ResponseDetail.TCP.value, 'Port': self.test_port[i], 'Time':(time.time()-t_all)}
            except:
                self.Logger.debug ('Status 2: %s | IP: %s | Port: %s | Detail: %s | Time: %s' % (ResponseStatus.KO.value,self.ipaddress.compressed,self.test_port[i],ResponseDetail.TCP.value,(time.time() - t_start)))
                pass
        try:
            t_start = time.time()
            response = os.system(self.ping_command + ' -q -W' + str(self.timeout) + ' -c' + self.ping_count + ' ' + self.ipaddress.compressed + ' > /dev/null 2>&1')
            if response == 0:
                t_end = time.time()
                self.Logger.debug ('Status: %s | IP: %s | Port: %s | Detail: %s | Time: %s' % (ResponseStatus.OK.value,self.ipaddress.compressed,23,ResponseDetail.ICMP.value,(time.time() - t_start)))
                return {'Status': ResponseStatus.OK.value, 'Detail': ResponseDetail.ICMP.value, 'Port': '23', 'Time':(time.time()-t_all)}
        except:
            pass

        self.Logger.debug ('Status: %s | IP: %s | Port: %s | Detail: %s | Time: %s' % (ResponseStatus.KO.value,self.ipaddress.compressed,23,ResponseDetail.ICMP.value,(time.time() - t_start)))
        return {'Status': ResponseStatus.KO.value, 'Detail': ResponseDetail.ICMP.value, 'Port': '23', 'Time':(time.time()-t_all)}
