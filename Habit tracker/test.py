import certifi
from pymongo import MongoClient

uri = "mongodb+srv://helenalyq1023_db_user:Uj28BgryGB0K7WIW@habittracker.xmvpoxl.mongodb.net/?appName=HabitTracker"

client = MongoClient(uri, tlsCAFile=certifi.where())

print(client.list_database_names())