import json
import sched
import time
from random import randrange
from threading import Thread
from firebase_admin import credentials, initialize_app, messaging

from imdb_parser import get_actor_info


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

        firebaseCredentials = credentials.Certificate('firebase_service_account_key.json')
        self.firebaseApp = initialize_app(firebaseCredentials)

    def addSubscription(self, actorId, firebaseToken):
        if firebaseToken is None or actorId is None:
            raise ValueError
        if not actorId.startswith('nm'):
            raise ValueError

        if actorId in self.subscriptions:
            self.subscriptions[actorId]['fireTokens'].append(firebaseToken)
        else:
            self.subscriptions[actorId] = {
                "fireTokens": [firebaseToken],
            }
            self._appendCheckerSchedule(actorId)
        self.saveSubscriptions()

    def removeSubscription(self, actorId, firebaseToken):
        if firebaseToken is None or actorId is None:
            raise ValueError

        if actorId in self.subscriptions and firebaseToken in self.subscriptions[actorId]['fireTokens']:
            if len(self.subscriptions[actorId]['fireTokens']) > 1:
                self.subscriptions[actorId]['fireTokens'].remove(firebaseToken)
            else:
                self.subscriptions.pop(actorId)
            self.saveSubscriptions()
        else:
            raise ValueError

    def checkActor(self, actorId):
        print(f'CHECK FOR {actorId}')
        if actorId not in self.subscriptions:
            raise NameError

        info = get_actor_info(actorId)
        count, completedCount, actorName, actorPicture, lastCompletedTitle, lastTitle = info[7], len(info[9]), info[0], info[4], info[8][0], info[10]
        save = False
        notification = None

        if 'count' not in self.subscriptions[actorId] or 'completedCount' not in self.subscriptions[actorId]:
            self.subscriptions[actorId]['count'] = count
            self.subscriptions[actorId]['completedCount'] = completedCount
            save = True
        else:
            if completedCount < self.subscriptions[actorId]['completedCount']:
                self.subscriptions[actorId]['completedCount'] = completedCount
                save = True
            elif completedCount > self.subscriptions[actorId]['completedCount']:
                notification = messaging.Notification(title=f'{actorName} has a new title upcoming!', body=f'Title named {lastCompletedTitle["title"]} going to be released soon', image=actorPicture)
                self.subscriptions[actorId]['completedCount'] = completedCount
                save = True

            if count < self.subscriptions[actorId]['count']:
                self.subscriptions[actorId]['count'] = count
                save = True
            elif count > self.subscriptions[actorId]['count']:
                notification = messaging.Notification(title=f'{actorName} just got a new title!', body=f'New title {lastCompletedTitle} going to be a hit in a few years', image=actorPicture)
                self.subscriptions[actorId]['count'] = count
                save = True

        if save:
            self.saveSubscriptions()

        self._appendCheckerSchedule(actorId, randomTime=False)

        if notification:
            android = messaging.AndroidConfig(notification=messaging.AndroidNotification(default_sound='', default_vibrate_timings=True, icon='launch_logo'), priority="high")
            msg = messaging.MulticastMessage(tokens=self.subscriptions[actorId]['fireTokens'], notification=notification, android=android, data={"click_action": "FLUTTER_NOTIFICATION_CLICK"})
            messaging.send_multicast(msg)

    def saveSubscriptions(self):
        dumpString = json.dumps(self.subscriptions)
        with open('subscriptions.json', 'w') as subsFile:
            subsFile.write(dumpString)


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