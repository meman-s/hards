import pymongo


client = None


def init_mongo(url):
    global client
    client = pymongo.MongoClient(url)


def close_mongo():
    global client
    if client:
        client.close()
        client = None
