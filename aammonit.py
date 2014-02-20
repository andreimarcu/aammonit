#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import logging
from time import sleep
import config


class Aammonit(object):
    def __init__(self, config):
        self.config = config
        self.states = []

    def start(self):
        while True:
            self.check_services()

    def stop(self):
        for notifier in self.config.to_notify:
            notifier.terminate()

    def notify(self, message):
        for notifier in config.to_notify:
            notifier.send_notification(message)

    def check_services(self):
        for service in self.config.to_check:
            try:
                if service.online():
                    if str(service) in self.states:
                        self.states.remove(str(service))
                        self.notify(str(service) + " is now back online.")

                else:
                    if str(service) in self.states:
                        pass
                    else:
                        self.states.append(str(service))
                        self.notify(service.status())

            except Exception as e:
                self.notify(str(e))

            sleep(self.config.interval)


if __name__ == '__main__':

    am = Aammonit(config)

    try:
        am.start()
    except KeyboardInterrupt:
        am.stop()
    except:
        am.stop()
        raise
