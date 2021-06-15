import json
import sched
import time
from random import randrange
from threading import Thread

from firebase_admin import credentials, initialize_app, messaging


class CheckerScheduler:
    def _appendCheckerSchedule(self, actorId, randomTime=True):
        if actorId is not None and type(actorId) is str and actorId.startswith('nm'):
            print(f'New schedule item: {actorId} details: {self.subscriptions[actorId]}')

            # schedulerHasStopped = self.scheduler.empty()
            self.scheduler.enter(delay=randrange(600, 86400) if randomTime else 86400, priority=1,
                                 action=self.checkActor, argument=(actorId,))

            # if schedulerHasStopped:  # TODO: change scheduler to something more reliable. UPD: maybe not, but scheduler needs more testing
                # Thread(target=self.scheduler.run, daemon=True).start()
        else:
            raise ValueError

    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)

        with open('subscriptions.json', 'r') as subsFile:
            self.subscriptions = json.loads(subsFile.read())

        for actor in self.subscriptions.keys():
            self._appendCheckerSchedule(actor)

        Thread(target=self.scheduler.run, daemon=True).start()

        firebaseCredentials = credentials.Certificate("firebase_service_account_key.json")
        self.firebaseApp = initialize_app(firebaseCredentials)

    def addSubscription(self, firebaseToken, actorId):
        if firebaseToken is None or actorId is None:
            raise ValueError

        if actorId in self.subscriptions:
            self.subscriptions[actorId]['fireTokens'].append(firebaseToken)
        else:
            self.subscriptions[actorId] = {
                "fireTokens": [firebaseToken],
            }
            self._appendCheckerSchedule(actorId)

    def checkActor(self, actorId):
        print(f'CHECK FOR {actorId}')
        if actorId not in self.subscriptions:
            raise NameError

        # TODO: call parser
        count, completedCount = 10, 1  # parser result
        if count > self.subscriptions[actorId]['count']:
            # TODO: notify all firebase tokens about a future title (about 1-3 years before release)
            pass
        if completedCount > self.subscriptions[actorId]['completedCount']:
            # TODO: notify all firebase tokens about upcoming title (usually in next 6 months or so)
            pass

        self._appendCheckerSchedule(actorId, randomTime=False)


"""if __name__ == '__main__':
    checkerScheduler = CheckerScheduler(
        subscriptions={
            "nm0413168": {
                "fireTokens": [],
                "count": 0,
                "completedCount": 0,
             },
        },
    )
"""