from connection.database import connect_to_mongo

db = connect_to_mongo()

usuarios_collection = db["usuarios"]

