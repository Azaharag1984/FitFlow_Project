from fastapi import FastAPI
from app.connection.database import connect_to_mongo, close_mongo_connection

# Create the FastAPI application instance
app = FastAPI()


# Startup event that runs when the application starts
@app.on_event("startup")
def startup_db_client():
    connect_to_mongo()  # Connect to MongoDB when the application starts
    print("Successfully connected to MongoDB")

# Shutdown event that runs when the application shuts down
@app.on_event("shutdown")
def shutdown_db_client():
    close_mongo_connection()  # Close the connection to MongoDB when the application shuts down
    print("MongoDB connection closed")

# Test route
@app.get("/")
def read_root():
    return {"message": "The API is working correctly!"}