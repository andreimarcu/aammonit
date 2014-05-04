import requests
import smtplib
import subprocess
import socket


class Service(object):
    up = False
    error = None

    def __str__(self):
        raise NotImplementedError()

    def online(self):
        raise NotImplementedError()

    def status(self):
        if self.up:
            return str(self) + " is up"
        else:
            if self.error:
                return str(self) + " is down: " + self.error
            else:
                return str(self) + " is down."


class Http(Service):
    def __init__(self, url):
        self.url = url
        self.error = None

    def __str__(self):
        return "HTTP check for " + self.url

    def online(self):
        try:
            resp = requests.get(self.url)
            if resp.status_code == 200:
                self.up = True
            else:
                self.up = False
                self.error = "Status code is: " + str(resp.status_code)

        except Exception as e:
            self.up = False
            self.error = str(e)

        return self.up

class Port(Service):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __str__(self):
        return "PORT check of " + self.host + " " + str(self.port) 

    def online(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.host, self.port))
            if result == 0:
               self.up = True
            else:
               raise Exception
        except:
            self.up = False

        return self.up

class Ping(Service):
    def __init__(self, host):
        self.host = host

    def __str__(self):
        return "PING " + self.host

    def online(self):
        try:
            subprocess.check_call(["ping", "-c", "2", self.host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.up = True
        except:
            self.up = False

        return self.up


class Ping6(Service):
    def __init__(self, host):
        self.host = host

    def __str__(self):
        return "PING6 " + self.host

    def online(self):
        try:
            subprocess.check_call(["ping6", "-c", "2", self.host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.up = True
        except:
            self.up = False

        return self.up


class Smtp(Service):
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

    def __str__(self):
        return "SMTP check for " + self.server + ":" + str(self.port)

    def online(self):
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
            self.up = True

        except Exception as e:
            self.error = str(e)
            self.up = False

        return self.up


class Fake(Service):
    """
    Useful for debugging
    fails it fail == True
    """
    def __init__(self, fail, name):
        self.name = name
        self.fail = fail

    def __str__(self):
        return "FAKE " + self.name

    def online(self):
        self.up = not self.fail

        return self.up

class FakeThree(Service):
    """
    Fails every three iterations, starting with the first one.
    Useful to test state.
    """
    def __init__(self, name):
        self.name = name
        self.iteration = 0

    def __str__(self):
        return "FAKETHREE " + self.name

    def online(self):
        if self.iteration % 3 == 0:
            self.iteration += 1
            self.up = False
        else:
            self.iteration += 1
            self.up = True

        return self.up
