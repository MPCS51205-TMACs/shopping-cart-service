from abc import ABC, abstractmethod
from typing import Dict, Set, Optional
from domain.cart import *
from pymongo import MongoClient
from pymongo.database import Database, Collection
from pymongo.errors import AutoReconnect

class ReceiptRepository(ABC):

    @abstractmethod
    def get(self, receipt_id: str) -> Optional[Receipt]:
        pass

    @abstractmethod
    def save(self, receipt: Receipt) -> None:
        pass

class InMemoryReceiptRepository(ReceiptRepository):
    
    def __init__(self) -> None:
        self._receipts : Dict[str,Receipt] = dict()

    def get(self, receipt_id: str) -> Optional[Receipt]:
        if receipt_id in self._receipts:
            return self._receipts[receipt_id]

    def save(self, receipt: Receipt) -> None:
        self._receipts[receipt._receipt_id] = receipt

class MongoDbReceiptRepository(ReceiptRepository):

    DATABASE_NAME = "cart_db" # name of mongo db database for this service
    RECEIPTS_COLLECTION_NAME = "receipts" 
    # (typical) MONGO_DB_CONNECTION_PATH = "mongodb://localhost:27017/"
    
    def __init__(self, hostname: str, port: str= "27017") -> None:
        self.mongo_db_connection_url = f"mongodb://{hostname}:{port}/"

        # establish connection to where mongo database lives (will live)
        print("[MongoDbCartRepository] establishing connection to MongoDB server...")
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
        if self.RECEIPTS_COLLECTION_NAME not in self.my_db.list_collection_names():
            print(f"collection '{self.RECEIPTS_COLLECTION_NAME}' does not exist; creating...")
            receipts_collection = self.my_db.create_collection(self.RECEIPTS_COLLECTION_NAME)
        else:
            print(f"collection '{self.RECEIPTS_COLLECTION_NAME}' appears to already exist")
            receipts_collection = self.my_db[self.RECEIPTS_COLLECTION_NAME]

        
    def _get_receipts_collection(self) -> Collection:
        try:
            return self.my_db[self.RECEIPTS_COLLECTION_NAME]
        except AutoReconnect:
            self._reestablish_connection()

    def get(self, receipt_id: str) -> Optional[Receipt]:
        """returns receipt based on id"""
        print(f"[MongoDbCartItemsRepository] getting Receipt object, receipt_id={receipt_id} to MongoDb")
        query_doc = {
            "receipt_id": receipt_id
        }

        try:
            receipts_collection = self._get_receipts_collection()
            data = receipts_collection.find_one(query_doc)
        except AutoReconnect:
            self._reestablish_connection()
            receipts_collection = self._get_receipts_collection()
            data = receipts_collection.find_one(query_doc)

        # print(f"what is in the db: (saved receipt_id={receipt_id})")
        # for document in cursor:
        #     print(document)

        if data:
            return Receipt.from_data_dict_to_receipt(data["receipt"])
        else:
            return None

    def save(self, receipt: Receipt) -> None:
        """saves the Receipt object"""
        print(f"[MongoDbCartItemsRepository] saving Receipt object, receipt_id={receipt._receipt_id} to MongoDb")
        doc = {
            "receipt_id": receipt._receipt_id,
            "receipt": receipt.to_data_dict()
        }

        try:
            receipts_collection = self._get_receipts_collection()
            data = receipts_collection.replace_one({ 'receipt_id': receipt._receipt_id }, doc, upsert=True)
        except AutoReconnect:
            self._reestablish_connection()
            receipts_collection = self._get_receipts_collection()
            data = receipts_collection.replace_one({ 'receipt_id': receipt._receipt_id }, doc, upsert=True)

        cursor = receipts_collection.find({})
        print(f"after saving, what is in the db: (saved receipt_id={receipt._receipt_id})")
        for document in cursor:
            print(document)

    def _reestablish_connection(self):
        self.client = MongoClient(self.mongo_db_connection_url)
        self.my_db = self.client[self.DATABASE_NAME]
