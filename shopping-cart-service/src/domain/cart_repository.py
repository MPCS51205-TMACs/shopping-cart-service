from abc import ABC, abstractmethod
from typing import Dict, Set, Optional
from domain.cart import *
from pymongo import MongoClient
from pymongo.database import Database, Collection
from pprint import pprint # to print bson like data prettier

class CartRepository(ABC):

    @abstractmethod
    def get_cart(self, user_id: str) -> Cart:
        pass

    @abstractmethod
    def save_cart(self, cart: Cart) -> None:
        pass

    @abstractmethod
    def get_carts(self, containing_item_ids: Set[str]) -> List[Cart]:
        pass


class InMemoryCartRepository(CartRepository):

    def __init__(self) -> None:
        super().__init__()
        self._carts: Dict[str,Cart] = dict() 

    def get_cart(self, user_id: str) -> Cart:
        if user_id in self._carts:
            return self._carts[user_id]
        else:
            return Cart(user_id, [])

    def get_carts(self, containing_item_ids: Set[str]) -> List[Cart]:
        carts = []
        for _, cart in self._carts:
            for item_id in containing_item_ids:
                if item_id in cart:
                    carts.append(cart)
        return carts

    def save_cart(self, cart: Cart):
        self._carts[cart._user_id] = cart # works for both add new and update

# class MongoDbCartRepository:

#     DATABASE_NAME = "cart_db" # name of mongo db database for this service
#     BOUGHT_ITEMS_COLLECTION_NAME = "cart_items" 
#     # (typical) MONGO_DB_CONNECTION_PATH = "mongodb://localhost:27017/"
    
#     def __init__(self, hostname: str, port: str= "27017") -> None:
#         self.mongo_db_connection_url = f"mongodb://{hostname}:{port}/"

#         # establish connection to where mongo database lives (will live)
#         print("[MongoDbCartRepository] establishing connection to MongoDB server...")
#         self.client = MongoClient(self.mongo_db_connection_url)

#         # # drop database (if already exists)?? optional
#         # print("dropping database '{DATABASE_NAME}'")
#         # self.client.drop_database(DATABASE_NAME)

#         # create database if it doesn't already exist (this done automatically?)
#         if self.DATABASE_NAME not in self.client.list_database_names():
#             print(f"database '{self.DATABASE_NAME}' does not exist")
#         else:
#             print(f"database '{self.DATABASE_NAME}' appears to already exist")
#         self.my_db = self.client[self.DATABASE_NAME]

#         # create collection to store auction data
#         if self.BOUGHT_ITEMS_COLLECTION_NAME not in self.my_db.list_collection_names():
#             print(f"collection '{self.BOUGHT_ITEMS_COLLECTION_NAME}' does not exist; creating...")
#             cart_items_collection = self.my_db.create_collection(self.BOUGHT_ITEMS_COLLECTION_NAME)
#         else:
#             print(f"collection '{self.BOUGHT_ITEMS_COLLECTION_NAME}' appears to already exist")
#             cart_items_collection = self.my_db[self.BOUGHT_ITEMS_COLLECTION_NAME]


#     def get_cart(self, user_id: str) -> Cart:
#         if user_id in self._carts:
#             return self._carts[user_id]
#         else:
#             return Cart(user_id, [])

#     def get_carts(self, containing_item_ids: Set[str]) -> List[Cart]:
#         carts = []
#         for _, cart in self._carts:
#             for item_id in containing_item_ids:
#                 if item_id in cart:
#                     carts.append(cart)
#         return carts

#     def save_cart(self, cart: Cart):
#         self._carts[cart._user_id] = cart # works for both add new and update







#     def add(self, item_id: str) -> None:
#         bought_items_collection = self._get_bought_items_collection()
#         document = dict()
#         bought_items_collection.update_one({ '_id' : item_id}, { '$set': document }, upsert=True)

#     def has(self, item_id: str) -> bool:
#         query_doc = {
#             "item_id": item_id
#         }
#         bought_items_collection = self._get_bought_items_collection()
#         data = bought_items_collection.find_one(query_doc)
#         return True if data else False

        
#     def _get_bought_items_collection(self) -> Collection:
#         return self.my_db[self.BOUGHT_ITEMS_COLLECTION_NAME]

#     def check_server_status(self):
#         serverStatusResult = self.client[self.DATABASE_NAME].command("serverStatus")
#         pprint(serverStatusResult)






    # def get_auction(self, item_id: str) -> Optional[ClosedAuction]:
    #     query_doc = {
    #         "item_id": item_id
    #     }
    #     auction_collection = self._get_auction_collection()
    #     data = auction_collection.find_one(query_doc)
    #     return self._mongoDataToClosedAuction(data) if data else None

    # def save_auction(self, auction: ClosedAuction):
#         auction_collection = self._get_auction_collection()
#         document = auction.convert_to_dict_w_datetimes()
#         auction_collection.update_one({ '_id' : auction._item_id}, { '$set': document }, upsert=True)

#     def _mongoDataToClosedAuction(self, data: Dict) -> ClosedAuction:

#         data["dt_start_time"] = utils.toDatetimeFromStr(data["str_start_time"])
#         data["dt_end_time"] = utils.toDatetimeFromStr(data["str_end_time"])

#         for bid in data["bids"]:
#             bid["dt_time_received"] = utils.toDatetimeFromStr(bid["str_time_received"])

#         if data["str_cancellation_time"]:
#             data["dt_cancellation_time"] = utils.toDatetimeFromStr(data["str_cancellation_time"])
#         else:
#             data["dt_cancellation_time"] = None

#         if data["str_finalized_time"]:
#             data["dt_finalized_time"] = utils.toDatetimeFromStr(data["str_finalized_time"])
#         else:
#             data["dt_finalized_time"] = None

#         if data["str_finalized_time"]:
#             data["dt_finalized_time"] = utils.toDatetimeFromStr(data["str_finalized_time"])
#         else:
#             data["dt_finalized_time"] = None

#         winning_bid = None
#         if "winning_bid" in data.keys():
#             bid_data = data["winning_bid"]
#             winning_bid = Bid(bid["bid_id"],bid["item_id"],bid["bidder_user_id"],bid["amount_in_cents"],bid["dt_time_received"],bid["active"])

#         bids: List[Bid] = []
#         for bid in data["bids"]:
#             bids.append(Bid(bid["bid_id"],bid["item_id"],bid["bidder_user_id"],bid["amount_in_cents"],bid["dt_time_received"],bid["active"]))

#         item_id : str = data["item_id"]
#         start_price_in_cents : int = data["start_price_in_cents"]
#         start_time : datetime.datetime = data["dt_start_time"]
#         end_time  : datetime.datetime = data["dt_end_time"]
#         cancellation_time  : Optional[datetime.datetime] = data["dt_cancellation_time"] if data["dt_cancellation_time"] else None
#         finalized_time  : datetime.datetime = data["dt_finalized_time"]

#         new_closed_auction = ClosedAuction(item_id,start_price_in_cents,start_time,end_time,cancellation_time,finalized_time,bids, winning_bid)
#         return new_closed_auction


# class MongoDbAuctionRepository(AuctionRepository):



#     def __init__(self, hostname: str, port: str= "27017") -> None:

#         self.mongo_db_connection_url = f"mongodb://{hostname}:{port}/"
        
#         # establish connection to where mongo database lives (will live)
#         print("establishing connection to MongoDB server...")
#         self.client = MongoClient(self.mongo_db_connection_url)

#         # # drop database (if already exists)?? optional
#         # print("dropping database '{DATABASE_NAME}'")
#         # self.client.drop_database(DATABASE_NAME)

#         # create database if it doesn't already exist (this done automatically?)
#         if DATABASE_NAME not in self.client.list_database_names():
#             print(f"database '{DATABASE_NAME}' does not exist")
#         else:
#             print(f"database '{DATABASE_NAME}' appears to already exist")
#         self.my_db = self.client[DATABASE_NAME]

#         # create collection to store auction data
#         if AUCTION_COLLECTION_NAME not in self.my_db.list_collection_names():
#             print(f"collection '{AUCTION_COLLECTION_NAME}' does not exist; creating...")
#             auction_collection = self.my_db.create_collection(AUCTION_COLLECTION_NAME)
#         else:
#             print(f"collection '{AUCTION_COLLECTION_NAME}' appears to already exist")
#             auction_collection = self.my_db[AUCTION_COLLECTION_NAME]


#     def _get_auction_collection(self) -> Collection:
#         return self.my_db[AUCTION_COLLECTION_NAME]

#     def check_server_status(self):
#         serverStatusResult = self.client[DATABASE_NAME].command("serverStatus")
#         pprint(serverStatusResult)

#     def get_auction(self, item_id: str) -> Optional[ClosedAuction]:
#         query_doc = {
#             "item_id": item_id
#         }
#         auction_collection = self._get_auction_collection()
#         data = auction_collection.find_one(query_doc)
#         return self._mongoDataToClosedAuction(data) if data else None

#     def get_auctions(self, leftBound: Optional[datetime.datetime], rightBound: Optional[datetime.datetime], limit: Optional[int]=None) -> List[ClosedAuction]:
#         auction_collection = self._get_auction_collection()

#         if leftBound or rightBound:
#             if leftBound and rightBound:
#                 time_param = {'$lte': rightBound, '$gte': leftBound}
#             elif leftBound:
#                 time_param = {'$gte': leftBound}
#             else: # rightBound
#                 time_param = {'$lte': rightBound}
#             query_doc = { "end_time": time_param }
#         else:
#             query_doc = {} # getting all auctions (up to default limit)...

#         # retreive auctions
#         cursor = auction_collection.find(query_doc)
#         auctions : List[ClosedAuction] = []
#         for data in cursor:
#             closed_auction = self._mongoDataToClosedAuction(data)
#             auctions.append(closed_auction)

#         # order auctions by end time
#         _sort_auction_results(auctions)

#         # filter down number of results
#         if not limit:
#             limit = 10 # default max number of auctions returned
#         auction_list_trimmed = _limit_auction_results(auctions,limit,toSort=False)

#         return auction_list_trimmed

#     def save_auction(self, auction: ClosedAuction):
#         auction_collection = self._get_auction_collection()
#         document = auction.convert_to_dict_w_datetimes()
#         auction_collection.update_one({ '_id' : auction._item_id}, { '$set': document }, upsert=True)

#     def _mongoDataToClosedAuction(self, data: Dict) -> ClosedAuction:

#         data["dt_start_time"] = utils.toDatetimeFromStr(data["str_start_time"])
#         data["dt_end_time"] = utils.toDatetimeFromStr(data["str_end_time"])

#         for bid in data["bids"]:
#             bid["dt_time_received"] = utils.toDatetimeFromStr(bid["str_time_received"])

#         if data["str_cancellation_time"]:
#             data["dt_cancellation_time"] = utils.toDatetimeFromStr(data["str_cancellation_time"])
#         else:
#             data["dt_cancellation_time"] = None

#         if data["str_finalized_time"]:
#             data["dt_finalized_time"] = utils.toDatetimeFromStr(data["str_finalized_time"])
#         else:
#             data["dt_finalized_time"] = None

#         if data["str_finalized_time"]:
#             data["dt_finalized_time"] = utils.toDatetimeFromStr(data["str_finalized_time"])
#         else:
#             data["dt_finalized_time"] = None

#         winning_bid = None
#         if "winning_bid" in data.keys():
#             bid_data = data["winning_bid"]
#             winning_bid = Bid(bid["bid_id"],bid["item_id"],bid["bidder_user_id"],bid["amount_in_cents"],bid["dt_time_received"],bid["active"])

#         bids: List[Bid] = []
#         for bid in data["bids"]:
#             bids.append(Bid(bid["bid_id"],bid["item_id"],bid["bidder_user_id"],bid["amount_in_cents"],bid["dt_time_received"],bid["active"]))

#         item_id : str = data["item_id"]
#         start_price_in_cents : int = data["start_price_in_cents"]
#         start_time : datetime.datetime = data["dt_start_time"]
#         end_time  : datetime.datetime = data["dt_end_time"]
#         cancellation_time  : Optional[datetime.datetime] = data["dt_cancellation_time"] if data["dt_cancellation_time"] else None
#         finalized_time  : datetime.datetime = data["dt_finalized_time"]

#         new_closed_auction = ClosedAuction(item_id,start_price_in_cents,start_time,end_time,cancellation_time,finalized_time,bids, winning_bid)
#         return new_closed_auction



# def _sort_auction_results(closed_auctions: List[ClosedAuction]):
#     """sorts the closed auctions sorted from ending the farthest back in time to most recent (last idx)."""
#     # sort closed auctions in ascending order by time of finalization
#     closed_auctions.sort(key=lambda ca: ca.get_end_time())
    
# def _limit_auction_results(closed_auctions: List[ClosedAuction], limit: int, toSort: bool=False) -> List[ClosedAuction]:
#     """Returns the most recently closed auctions up till limit into the past."""
#     if len(closed_auctions) > limit:
#         if toSort:
#             _sort_auction_results(closed_auctions)
#         closed_auctions = closed_auctions[len(closed_auctions)-limit:] # keep most recently ended closed-auctions until limit
#     return closed_auctions








if __name__ == "__main__":
    carts = rand_carts(quantity=4)
    a_name = carts[0]._user_id
    a_itemid = list(carts[0]._items)[0].item_id
    print("name :", a_name)
    print("itemid :", a_itemid)

    repo = InMemoryCartRepository()

    for cart in carts:
        print("saving ",cart)
        repo.save_cart(cart)

    print(repo.get_cart(a_name))