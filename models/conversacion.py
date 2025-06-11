from connection.database import connect_to_mongo

db = connect_to_mongo()

conversaciones_collection = db["conversaciones"]

