import irc.client
import sleekxmpp
import threading
import smtplib
import requests
import Queue
import ssl

class Notifier(object):
    def send_notification(self, message):
        raise NotImplementedError()

    def terminate(self):
        pass


class Print(Notifier):
    """
    Prints to terminal where aammonit is run
    """
    def send_notification(self, message):
        print message


class Pushover(Notifier):
    """
    Simple https://pushover.net/ notifier, needs user key and application token. 
    """
    def __init__(self, token, user):
        self.token = token
        self.user = user

    def send_notification(self, message):
        API_URL = "https://api.pushover.net/1/messages.json"

        data = {"token": self.token,
                "user": self.user,
                "message": message,
                }
        try:
            requests.post(API_URL, data=data)
        except Exception as e:
            print "Pushover notification failed: " + str(e)


class Irc(Notifier, threading.Thread):
    """
    IRC bot notifier. if "target" is a channel, he will join the channel on connect. 

    """
    def __init__(self, server, port, nickname, target, nickserv_pass=None, ssl=False):
            self.server = server
            self.port = port
            self.ssl = ssl
            self.nickname = nickname
            self.target = target
            self.nickserv_pass = nickserv_pass
            self.bot = None

            self.queue = Queue.Queue()
            self.running = threading.Event()
            self.running.set()

            threading.Thread.__init__(self)
            self.start()

    def run(self):
        self.bot = self.IrcBot(self.server, self.port, self.nickname, self.target, self.nickserv_pass, self.queue, self.running, self.ssl)
        self.bot.start()

    def terminate(self):
        self.running.clear()

    def send_notification(self, message):
        self.queue.put(message)
  
    class IrcBot(irc.client.SimpleIRCClient):
        def __init__(self, server, port, nickname, target, nickserv_pass, queue, running, use_ssl=False):
            irc.client.SimpleIRCClient.__init__(self)
            self.server = server
            self.port = port
            self.use_ssl = use_ssl
            self.nickname = nickname
            self.target = target
            self.nickserv_pass = nickserv_pass
            self.queue = queue
            self.running = running

            if self.use_ssl:
                ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
                self.connect(self.server, self.port, self.nickname, connect_factory=ssl_factory)
            else:
                self.connect(self.server, self.port, self.nickname)

        def on_welcome(self, connection, event):
            if self.nickserv_pass:
                self.connection.privmsg("Nickserv", "identify " + self.nickserv_pass)

            if irc.client.is_channel(self.target):
                connection.join(self.target)

        def on_join(self, connection, event):

            while self.running.is_set():
                try:
                    message = self.queue.get(False)
                    self.connection.privmsg(self.target, message)
                except:
                    pass

            self.connection.quit()

        def on_disconnect(self, connection, event):
            if self.running.is_set():
                self.connect(self.server, self.port, self.nickname)
            else:
                raise SystemExit()


class Xmpp(Notifier, sleekxmpp.ClientXMPP):
    """
    XMPP notifier, needs dnspython to auto-resolve the host. You may also manually specify it.
    """
    def __init__(self, jid, password, recipient, host=None, tls=True, ssl=False, port=5222):
        self.recipient = recipient

        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.start)
        self.use_signals(signals=['SIGHUP', 'SIGTERM', 'SIGINT'])

        address = (host, port) if host else None

        if self.connect(address=address, use_tls=tls, use_ssl=ssl):
            self.send_notification("XMPP notifier online.")
            self.process()

        else:
            raise Exception("Could not connect")

    def terminate(self):
        self.send_notification("XMPP notifier going offline.")
        self.disconnect(wait=True)

    def start(self, event):
        self.send_presence()
        self.get_roster()
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping

    def send_notification(self, message):
        self.send_message(mto=self.recipient, mbody=message, mtype='chat')


class Email(Notifier):
    def __init__(self, recipient, sender=None, server="localhost", port=25, username=None, password=None, ssl=False, starttls=False):
        self.recipient = recipient
        self.sender = sender if sender else username
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.ssl = ssl
        self.starttls = starttls

    def send_notification(self, message):
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

            message = """From: {0} 
To: {1}
Subject: aammonit notification

{2}
            """.format(self.sender, self.recipient, message)
            srv.sendmail(self.sender, [self.recipient], message)
            srv.quit()

        except Exception as e:
            print "Email notification failed: " + str(e)
