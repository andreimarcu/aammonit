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

    def check_services(self):
        for service in self.config.to_check:
            try:
                error = service.check()

                if error:
                    if service.description in self.states:
                        pass
                    else:
                        self.states.append(service.description)
                        self.notify(error)
                else:
                    if service.description in self.states:
                        self.states.remove(service.description)
                        self.notify(service.description + " is now operational.")
            except Exception as e:
                self.notify(str(e))

            sleep(self.config.interval)


    def notify(self, message):
        for notifier in config.to_notify:
            notifier.send_notification(message)


if __name__ == '__main__':

    am = Aammonit(config)

    try:
        am.start()
    except KeyboardInterrupt:
        am.stop()
        pass
    except:
        am.stop()
        raise
