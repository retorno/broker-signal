import pyrebase
import os
from datetime import datetime

config = {
  "apiKey": os.environ.get('API_KEY_FIREBASE'),
  "authDomain": os.environ.get('AUTH_DOMAIN_FIREBASE'),
  "databaseURL": os.environ.get('DATA_BASE_URL_FIREBASE'),
  "storageBucket": os.environ.get('STORAGE_BUCKET_FIREBASE')
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()


def saveFirebase(stock= {}):
    day = datetime.today().strftime('%Y%m%d')
    hour = datetime.today().strftime('%H:%M:%S')
    recipe = stock.get('recipe')
    db.child("invest").child(day).update({'recipe': recipe})
    db.child("invest").child(day).child(hour).update(stock)