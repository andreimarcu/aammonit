import sleekxmpp
import smtplib


class Print(object):
    """
    Prints to terminal where aammonit is run
    """
    def send_notification(self, message):
        print message

    def terminate(self):
        pass


class Xmpp(sleekxmpp.ClientXMPP):
    """
    XMPP notifier, needs dnspython to auto-resolve the host. You may also manually specify it.
    """
    def __init__(self, jid, password, recipient, host=None, tls=True, ssl=False, port=5222):
        self.recipient = recipient

        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("message", self.received_message)
        self.add_event_handler("session_start", self.start)
        self.use_signals(signals=['SIGHUP', 'SIGTERM', 'SIGINT'])

        address = (host, port) if host else None

        if self.connect(address=address, use_tls=tls, use_ssl=ssl):
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
        self.send_notification("XMPP notifier online.")


    def received_message(self, message):
        if message['type'] in ('chat', 'normal'):
            if message["from"].split("/")[0] == self.recipient:
                self.send_notification("Hi " + str(message["from"]))


    def send_notification(self, message):
        self.send_message(mto=self.recipient, mbody=message, mtype='chat')



class Email(object):
    def __init__(self, recipient, sender=None, server="localhost", port=25, username=None, password=None, ssl=False, starttls=False):
        self.recipient = recipient
        self.sender = sender if sender else username
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.ssl = ssl
        self.starttls = starttls

    def terminate(self):
        pass

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
