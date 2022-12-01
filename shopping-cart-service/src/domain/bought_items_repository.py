from abc import ABC, abstractmethod
from typing import Dict, Set, Optional, Any, Tuple
from domain.cart import *
from pymongo import MongoClient
from pymongo.database import Database, Collection
from pprint import pprint # to print bson like data prettier
from pymongo.errors import AutoReconnect

class BoughtItemsRepository(ABC):

    @abstractmethod
    def add(self, item_id: str, receipt_id : str) -> None:
        pass

    @abstractmethod
    def has(self, item_id: str) -> bool:
        pass

    @abstractmethod
    def get(self, item_id: str) -> Tuple[Optional[str], Optional[str]]:
        pass

class InMemoryBoughtItemsRepository(BoughtItemsRepository):
    
    def __init__(self) -> None:
        self._bought_items : Set[str] = set()
        self._item_id_to_receipt_id  : Dict[str,str] = dict()

    def add(self, item_id: str, receipt_id : str) -> None:
        self._bought_items.add(item_id)
        self._item_id_to_receipt_id[item_id] = receipt_id

    def has(self, item_id: str) -> bool:
        return item_id in self._bought_items

    def get(self, item_id: str) -> Tuple[Optional[str], Optional[str]]:
        if self.has(item_id):
            receipt_id = self._item_id_to_receipt_id[item_id]
            if receipt_id:
                return item_id, receipt_id
        return (None,None)

class MongoDbBoughtItemsRepository(BoughtItemsRepository):

    DATABASE_NAME = "cart_db" # name of mongo db database for this service
    BOUGHT_ITEMS_COLLECTION_NAME = "bought_items" 
    # (typical) MONGO_DB_CONNECTION_PATH = "mongodb://localhost:27017/"
    
    def __init__(self, hostname: str, port: str= "27017") -> None:
        self.mongo_db_connection_url = f"mongodb://{hostname}:{port}/"

        # establish connection to where mongo database lives (will live)
        print("[MongoDbBoughtItemsRepository] establishing connection to MongoDB server...")
        self.client = MongoClient(self.mongo_db_connection_url)

        # # drop database (if already exists)?? optional
        # print("dropping database '{DATABASE_NAME}'")
        # self.client.drop_database(DATABASE_NAME)

        # create database if it doesn't already exist (this done automatically?)
        if self.DATABASE_NAME not in self.client.list_database_names():
            print(f"database '{self.DATABASE_NAME}' does not exist")
        else:
            print(f"database '{self.DATABASE_NAME}' appears to already exist")
        self.my_db = self.client[self.DATABASE_NAME]

        # create collection to store auction data
        if self.BOUGHT_ITEMS_COLLECTION_NAME not in self.my_db.list_collection_names():
            print(f"collection '{self.BOUGHT_ITEMS_COLLECTION_NAME}' does not exist; creating...")
            bought_items_collection = self.my_db.create_collection(self.BOUGHT_ITEMS_COLLECTION_NAME)
        else:
            print(f"collection '{self.BOUGHT_ITEMS_COLLECTION_NAME}' appears to already exist")
            bought_items_collection = self.my_db[self.BOUGHT_ITEMS_COLLECTION_NAME]

    def add(self, item_id: str, receipt_id: str) -> None:
        bought_items_collection = self._get_bought_items_collection()
        document = {
            "item_id": item_id,
            "receipt_id": receipt_id
        }
        bought_items_collection.update_one({ '_id' : item_id}, { '$set': document }, upsert=True)

    def has(self, item_id: str) -> bool:
        query_doc = {
            "item_id": item_id
        }
        try:
            bought_items_collection = self._get_bought_items_collection()
            data = bought_items_collection.find_one(query_doc)
        except AutoReconnect:
            self._reestablish_connection()
            bought_items_collection = self._get_bought_items_collection()
            data = bought_items_collection.find_one(query_doc)
        return True if data else False

    def get(self, item_id: str) -> Tuple[Optional[str], Optional[str]]:
        query_doc = {
            "item_id": item_id
        }
        try:
            bought_items_collection = self._get_bought_items_collection()
            data = bought_items_collection.find_one(query_doc)
        except AutoReconnect:
            self._reestablish_connection()
            bought_items_collection = self._get_bought_items_collection()
            data = bought_items_collection.find_one(query_doc)
        if data:
            return data["item_id"], data["receipt_id"]
        return (None,None)
        
    def _get_bought_items_collection(self) -> Collection:
        try:
            return self.my_db[self.BOUGHT_ITEMS_COLLECTION_NAME]
        except AutoReconnect:
            self._reestablish_connection()

    def check_server_status(self):
        serverStatusResult = self.client[self.DATABASE_NAME].command("serverStatus")
        pprint(serverStatusResult)

    def _reestablish_connection(self):
        self.client = MongoClient(self.mongo_db_connection_url)
        self.my_db = self.client[self.DATABASE_NAME]
