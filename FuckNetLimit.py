#!/usr/bin/python
# coding=utf-8

import time
import sys
import socket
import os
import codecs
import urllib2
import locale
import platform
import subprocess
from ConfigParser import ConfigParser

IP_PREFIX = "10.104.171."
digits_history = {1, 2, 255}
last_available_ip = []
os_name = platform.system().lower()
CONFIG_PATH = os.path.normpath(os.path.expanduser("~/.fn.conf"))
OS_WINDOWS = 'windows'
OS_MAC = 'darwin'
OS_LINUX = 'linux'


def get_default_nic_name():
    if os_name == OS_MAC:
        return u"USB 10/100/1000 LAN"
    elif os_name == OS_LINUX:
        return u'eth0'
    elif os_name == OS_WINDOWS:
        return u'本地连接'
    else:
        raise Exception('platform {} not support'.format(os_name))


def load_nic_name():
    if not os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            f.write(u'''[root]
nic_name={}
'''.format(get_default_nic_name()).encode('utf-8'))

    parser = ConfigParser()
    with codecs.open(CONFIG_PATH, 'r', 'utf-8') as f:
        parser.readfp(f, CONFIG_PATH)
    return parser.get('root', 'nic_name')


def detect_blocked():
    return urllib2.urlopen('http://www.baidu.com').read().decode('UTF-8').find(u'信息工程大学') > 0


def detect_used_ip():
    for line in os.popen('nmap -PR -sn -n 10.104.171.0/24').readlines():
        if not line.strip().startswith('Nmap'):
            continue
        ip = line.split()[4]
        if ip[0].isdigit():
            yield ip


def detect_available_ip_list():
    used_digits = set([int(ip.split('.')[3]) for ip in detect_used_ip()])
    available_digits = set(range(1, 255)) - used_digits - digits_history
    if not len(available_digits):
        return []

    return map(lambda x: IP_PREFIX + str(x), sorted(list(available_digits)))


def detect_available_ip():
    global last_available_ip
    used_digits = set([int(ip.split('.')[3]) for ip in detect_used_ip()])
    available_digits = set(range(1, 255)) - used_digits - digits_history
    if not len(available_digits):
        return None
    digit = list(available_digits)[0]
    digits_history.add(digit)
    last_available_ip = available_digits
    return IP_PREFIX + str(digit)


def load_config_string():
    if os_name == OS_MAC:
        return u'networksetup -setmanual {0} {1} 255.255.255.0 10.104.171.1'
    elif os_name == OS_LINUX:
        return u'ifconfig {0} {1}/24\nroute add default 10.104.171.1'
    elif os_name == OS_WINDOWS:
        return u'netsh -c interface ip set address "{0}" static addr={1} mask=255.255.255.0 gateway=10.104.171.1'
    else:
        raise Exception('platform {} not support'.format(os_name))


def change_ip(ip):
    nic_name = load_nic_name()
    config_string = load_config_string()
    commands = config_string.format(nic_name, ip).encode(locale.getpreferredencoding()).split('\n')
    for command in commands:
        subprocess.check_call(command)


def main():
    MAX_ERROR = 4
    error_count = 0
    while True:
        try:
            while not detect_blocked():
                error_count = 0
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(10)
            print '\nblocked'
            ip = None
            while not ip:
                ip = detect_available_ip()
            print "change ip to", ip
            change_ip(ip)
            time.sleep(10)
        except Exception as ex:
            if str(ex).find("timed out") >= 0:
                sys.stdout.write('x')
                sys.stdout.flush()
            elif str(ex).find("[Errno 8]") >= 0:
                sys.stdout.write('o')
                error_count += 1
                if error_count >= MAX_ERROR and last_available_ip and len(last_available_ip):
                    digit = list(last_available_ip)[0]
                    last_available_ip.remove(digit)
                    ip = IP_PREFIX + str(digit)
                    print '\nchange ip to', ip
                    change_ip(ip)
                    error_count = 0
            else:
                print >> sys.stderr, ex


if __name__ == '__main__':
    socket.setdefaulttimeout(20)
    # main()

    ip_list = detect_available_ip_list()
    if len(sys.argv) == 2:
        index = int(sys.argv[1])
    else:
        for i, ip in enumerate(ip_list):
            print "{0}: {1}".format(i, ip)
        index = raw_input("index of IP to set:")
        index = int(index)

    ip = ip_list[index]
    print 'change ip to', ip
    change_ip(ip)
