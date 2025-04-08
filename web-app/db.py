"""docstring"""

import pymongo
from dotenv import load_dotenv
load_dotenv()

connection = pymongo.MongoClient("mongodb://localhost:27017/")

db = connection["epic-metal-machine"]

"""

file = {
    text: String,
    timestamp: Datetime
}


"""
