from connection.database import connect_to_mongo

db = connect_to_mongo()

ejercicios_collection = db["ejercicios"]




