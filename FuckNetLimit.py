#!/usr/bin/python
# coding=utf-8
import time
import sys
import socket
import os
import urllib2
import platform

IP_PREFIX = "10.104.171."
digits_history = {1, 2, 255}
last_available_ip = None


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


def change_ip(ip):
    os_name = platform.system().lower()
    if os_name == 'darwin':
        os.popen('networksetup -setmanual "USB 10/100/1000 LAN" {0} 255.255.255.0 10.104.171.1'.format(ip)).read()
    elif os_name == 'linux':
        os.popen('ifconfig eth0 {0}/24'.format(ip)).read()
        os.popen('route add default gw 10.104.171.1'.format(ip)).read()


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
                print >>sys.stderr, ex


if __name__ == '__main__':
    socket.setdefaulttimeout(20)
    #main()
    import sys
    from pprint import pprint
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
