import json
import sched
import time
from random import randrange

#class Subscription:
#    def __init__(self, actorId, firebaseTokens):


class CheckerScheduler:
    def __init__(self, subscriptions=None):
        if subscriptions is None:
            subscriptions = []
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.subscriptions = subscriptions

        for subscription in subscriptions:
            self.scheduler.enter(delay=randrange(60, 86400), action=)

    def addSubscription(self, firebaseToken, actorId):
        if firebaseToken is None or actorId is None:
            raise ValueError


    def checkActor(self, actorId):
        # TODO: call parser
        count,completedCount = 10,1 # parser result
        if count >

if __name__ == '__main__':
    checkerScheduler = CheckerScheduler(
        subscriptions={
            "nm0413168": {
                "fireTokens": [],
                "count": 0,
                "completedCount": 0,
             },
        },
    )
