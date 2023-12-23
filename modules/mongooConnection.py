from pymongo.mongo_client import MongoClient
# Create a new client and connect to the server
from modules.parser import mongoConfig
import enum
from motor.motor_asyncio import AsyncIOMotorClient
uri = mongoConfig['uri']
database_name:str = mongoConfig['database']
# Send a ping to confirm a successful connection
def testConn(uri:str):
    try:
        client = MongoClient(uri)
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)


def executeMongoQueyWithReturn(collection_name:str, findMethod:int, query:dict):
    try:
        uri = mongoConfig['uri']
        database_name:str = mongoConfig['database']
        # Connect to MongoDB using the provided URI
        client = MongoClient(uri)

        # Access the specified database and collection
        database = client[database_name]
        collection = database[collection_name]

        # Perform the query
        if findMethod == 1:
            result = collection.find_one(query)
        else:
            result = collection.find(query)
        return result
    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the MongoDB connection
        if client:
            client.close()

def executeMongoQueyInsert(collection_name:str, user_document:dict):
    try:
        uri = mongoConfig['uri']
        database_name:str = mongoConfig['database']
        # Connect to MongoDB using the provided URI
        client = MongoClient(uri)

        # Access the specified database and collection
        database = client[database_name]
        collection = database[collection_name]

        # Perform the query
        try : 
            collection.insert_one(user_document)
            return True
        except : return {"message" : "Unable to insert Record"}

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the MongoDB connection
        if client:
            client.close()

def getMongoConnection():
    try:
        uri = mongoConfig['uri']
        database_name:str = mongoConfig['database']
        # Connect to MongoDB using the provided URI
        client = AsyncIOMotorClient(uri)
        db = client[database_name]
        return client, db
    except:
        raise ConnectionRefusedError("Failed to connect to MongoDB server.")
    # finally:
    #     if client:
    #         client.close()