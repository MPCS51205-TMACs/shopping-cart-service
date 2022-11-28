from __future__ import annotations
from typing import Tuple
from domain.cart import *
from domain.cart_repository import *
from domain.item_repository import *

class CompositeCartRepository(CartRepository):

    def __init__(self, item_detail_repo: ItemRepository, cart_item_repo: CartItemsRepository) -> None:
        super().__init__()
        self._item_detail_repo = item_detail_repo
        self._cart_item_repo = cart_item_repo

    def get_cart(self, user_id: str) -> Cart:
        relevant_item_ids = self._cart_item_repo.get_item_ids(user_id) # the items in his cart
        items = self._item_detail_repo.get_items(relevant_item_ids)
        return Cart(user_id,items)

    def save_cart(self, cart: Cart) -> None:
        # just save the knowledge of the item_ids in his cart
        self._cart_item_repo.save_item_ids(cart._user_id,[item.item_id for item in cart._items])

    def get_carts(self, containing_item_ids: Set[str]) -> List[Tuple[Cart,List[str]]]:
        """
        returns all carts that contain a non-empty subset of item_ids from a set of item_ids;
        returns a list of ordered tuples containing (Cart, List of matching itemds)
        """
        users_and_items = self._cart_item_repo.get_user_item_mapping(containing_item_ids)
        carts_and_items : List[Tuple[Cart,List[str]]] = []
        for user, matching_items in users_and_items.items():
            cart = self._cart_item_repo(user)
            carts_and_items.append( (cart,matching_items))
        return carts_and_items

class CartItemsRepository(ABC):

    @abstractmethod
    def get_item_ids(self, user_id: str) -> List[str]:
        """returns list of item_id's that are in user's cart"""
        pass

    @abstractmethod
    def get_user_item_mapping(self, query_item_ids: List[str]) -> Dict[str,Set[str]]:
        """accepts a list of query_item_ids and returns a mapping of user_ids to item_ids; i.e.,
        a the item_ids from the set of query_item_ids that are in each user's cart"""
        pass

    @abstractmethod
    def save_item_ids(self, user_id:str,  item_ids: List[str]) -> None:
        """saves the list of item_id's that are in user's cart"""
        pass


class InMemoryCartItemsRepository(ABC):

    def __init__(self) -> None:
        super().__init__()
        self._cart_items : Dict[str,Set[str]] = dict() # user_id -> item_id

    def get_item_ids(self, user_id: str) -> List[str]:
        """returns list of item_id's that are in user's cart"""
        if user_id in self._cart_items:
            return list(self._cart_items[user_id])
        else:
            return []

    def get_user_item_mapping(self, query_item_ids: List[str]) -> Dict[str,Set[str]]:
        """accepts a list of query_item_ids and returns a mapping of user_ids to item_ids; i.e.,
        a list item_ids from the set of query_item_ids that are in each user's cart"""
        data = dict()
        for user_id, cart_item_ids in self._cart_items.values():
            matching_item_ids = set(query_item_ids).union(cart_item_ids)
            if len(matching_item_ids) > 0:
                data[user_id] = matching_item_ids
        return data

    def save_item_ids(self, user_id : str, item_ids: List[str]) -> None:
        """saves the list of item_id's that are in user's cart"""
        self._cart_items[user_id] = set(item_ids)



class MongoDbCartItemsRepository:

    DATABASE_NAME = "cart_db" # name of mongo db database for this service
    CART_ITEMS_COLLECTION_NAME = "cart_items" 
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
        if self.CART_ITEMS_COLLECTION_NAME not in self.my_db.list_collection_names():
            print(f"collection '{self.CART_ITEMS_COLLECTION_NAME}' does not exist; creating...")
            cart_items_collection = self.my_db.create_collection(self.CART_ITEMS_COLLECTION_NAME)
        else:
            print(f"collection '{self.CART_ITEMS_COLLECTION_NAME}' appears to already exist")
            cart_items_collection = self.my_db[self.CART_ITEMS_COLLECTION_NAME]

        
    def _get_cart_items_collection(self) -> Collection:
        return self.my_db[self.CART_ITEMS_COLLECTION_NAME]

    def get_item_ids(self, user_id: str) -> List[str]:
        """returns list of item_id's that are in user's cart"""
        query_doc = {
            "user_id": user_id
        }
        cart_items_collection = self._get_cart_items_collection()
        data = cart_items_collection.find_one(query_doc)
        if data:
            return data["item_ids"]
        else:
            return []

    def get_user_item_mapping(self, query_item_ids: List[str]) -> Dict[str,Set[str]]:
        """accepts a list of query_item_ids and returns a mapping of user_ids to item_ids; i.e.,
        a list item_ids from the set of query_item_ids that are in each user's cart"""
        unique_nums = set(query_item_ids)
        cart_items_collection = self._get_cart_items_collection()
        query_doc = { "item_ids": { "$elemMatch": { "$in": query_item_ids }}}
        docs = cart_items_collection.find(query_doc)
        results = dict()
        for doc in docs:
            user_id = doc["user_id"]
            item_ids = doc["item_ids"]
            matching_ids = set(item_ids).union(unique_nums)
            results[user_id] = matching_ids
        return results

    def save_item_ids(self, user_id : str, item_ids: List[str]) -> None:
        """saves the list of item_id's that are in user's cart"""
        doc = {
            "user_id": user_id,
            "item_ids": item_ids
        }
        cart_items_collection = self._get_cart_items_collection()
        data = cart_items_collection.replace_one({ 'user_id': user_id }, doc, )
        # data = cart_items_collection.updateOne({ 'user_id': user_id }, { '$addToSet': { "item_ids": {'$each': item_ids} } })


