import services
import notifiers


## Interval to go from one service check to another
interval = 5


to_notify = [
    notifiers.Print(),
    notifiers.Xmpp("username@jabber.example.org", "password", "destination@jabber.example.org"),
    notifiers.Irc("irc.oftc.net", 6697, "aammonit_bot", "#aammonit_bot", "nickserv_password", ssl=True),
    notifiers.Pushover("token", "user"),
    notifiers.Email("receiver@example.org", "aammonit@example.org", "mail.example", 465, "aammonit@example.net", "password", starttls=True),
    ]

to_check = [
    services.Http("https://google.com"),
    services.Ping("google.com"),
    services.Smtp("smtp.gmail.com", 587, False, True),
    services.Port("8.8.8.8", 53),
    ]

