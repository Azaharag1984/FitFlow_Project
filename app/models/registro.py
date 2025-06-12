from connection.database import connect_to_mongo

db = connect_to_mongo()

registros_collection = db["registros"]


