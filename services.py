import urllib2 
import smtplib
import subprocess
import socket


class Http(object):
    def __init__(self, url):
        self.url = url
        self.description = "HTTP check for " + self.url

    def check(self):
        try:
            urllib2.urlopen(self.url)
            return False
        except Exception as e:
            return self.description + " failed with: " + str(e)


class Port(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.description = "PORT check of " + self.host + " " + str(self.port) 

    def check(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.host, self.port))
            if result == 0:
               return False
            else:
               raise Exception
        except:
            return self.description + " failed"

class Ping(object):
    def __init__(self, host):
        self.host = host
        self.description = "PING " + self.host

    def check(self):
        try:
            subprocess.check_call(["ping", "-c", "4", self.host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return False
        except:
            return self.description + " failed"


class Smtp(object):
    """
    SMTP can test a simple connection, or a connection with user if you specify one.
    """
    def __init__(self, server, port=25, username=None, password=None, ssl=False, starttls=False):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.ssl = ssl
        self.starttls = starttls
        self.description = "SMTP check for " + self.server + ":" + str(self.port)


    def check(self):
        try:
            if self.ssl:
                srv = smtplib.SMTP_SSL(self.server, self.port)
            else:
                srv = smtplib.SMTP(self.server, self.port)

            srv.ehlo()

            if self.starttls:
                srv.starttls()
                srv.ehlo()

            if self.username:
                srv.login(self.username, self.password)


            srv.quit()
            return False
        except Exception as e:
            return self.description + " failed with: " + str(e)


class Fake(object):
    """
    Useful for debugging
    fails it fail == True
    """
    def __init__(self, fail, name):
        self.name = name
        self.fail = fail
        self.description = "FAKE " + self.name

    def check(self):
        if self.fail:
            return self.description + " failed"
        else:
            return False


class FakeThree(object):
    """
    Fails every three iterations, starting with the first one.
    Useful to test state.
    """
    def __init__(self, name):
        self.name = name
        self.iteration = 0
        self.description = "FAKETHREE " + self.name

    def check(self):
        if self.iteration % 3 == 0:
            self.iteration += 1
            return self.description + " failed"
        else:
            self.iteration += 1
            return False
