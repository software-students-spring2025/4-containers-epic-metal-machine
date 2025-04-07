import pymongo
from dotenv import load_dotenv
load_dotenv()


connection = pymongo.MongoClient("mongodb://localhost:27017/")

db = connection["epic_metal_machine"]

"""
image_to_convert = {
    image: String,
    transcription: String,
}

"""

