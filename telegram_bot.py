import datetime
import uuid
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from config import TELEGRAM_SEND_MESSAGE_URL

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
DAY_NAMES = u'DayNames'
CHATS = u'Chats'


class TelegramBot:
    def __init__(self):
        self.chat_id = None
        self.text = None
        self.incoming_message_text = None
        self.first_name = None
        self.last_name = None

    @staticmethod
    def get_names():
        dt = datetime.datetime.combine(datetime.date.today().replace(day=30), datetime.datetime.min.time())
        collection = db.collection(DAY_NAMES).where(u'Date', "==", dt).stream()
        try:
            doc = next(collection)
            day_names = DayNames.from_dict(doc.to_dict()).names
            names = ', '.join(day_names)
            return 'Сьогодні день ангела у ' + names + ', \n🎉Вітайте🥳'
        except:
            return 'Сьогодні немає іменин 😞'

    def parse_webhook_data(self, data):
        if u'message' in data:
            message = data['message']
            self.chat_id = message['chat']['id']
            if u'text' in message:
                self.incoming_message_text = message['text']
            if u'from' in message:
                if u'first_name' in message:
                    self.first_name = message['from']['first_name']
                if u'last_name' in message:
                    self.last_name = message['from']['last_name']

    def handle(self, req):
        self.parse_webhook_data(req)
        if self.incoming_message_text == '/dayNames':
            return self.send_message(self.get_names())
        elif self.incoming_message_text == '/setupCron':
            return self.setup_cron()
        return None

    def send_message(self, msg):
        response = requests.get(TELEGRAM_SEND_MESSAGE_URL.format(self.chat_id, msg))
        return True if response.status_code == 200 else False

    def add_new_names(self):
        dt = datetime.datetime.combine(datetime.date.today().replace(month=4, day=29), datetime.datetime.min.time())
        data = {
            u'Date': dt,
            u'Names': ['Ірини'
                       ]
        }
        uuid__set = db.collection(DAY_NAMES).document(str(uuid.uuid1())).set(data)
        print(uuid__set)

    def save_chat(self):
        data = {
            u'ChatId': self.chat_id,
            u'Enabled': True
        }
        db.collection(CHATS).document(str(uuid.uuid1())).set(data)

    def setup_cron(self):
        if self.chat_id is not None:
            self.save_chat()
            return self.send_message("Done!")
        else:
            return self.send_message("Something wrong 😞")


class DayNames(object):
    def __init__(self, names=None):
        if names is None:
            names = []
        self.names = names

    @staticmethod
    def from_dict(source):
        day_names = DayNames(source[u'Names'])
        return day_names

    def __repr__(self):
        return u'DayNames(Names={}'.format(self.names)
