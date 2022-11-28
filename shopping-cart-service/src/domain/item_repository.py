from abc import ABC, abstractmethod
from typing import Dict, Set, Optional
from domain.cart import *
from domain.cart_repository import *
import requests

class ItemRepository(ABC):

    def get_items(self, item_ids: List[str]) -> List[Item]:
        pass

    def add_items(self, item_ids: List[str]) -> None:
        pass

class HTTPProxyItemRepository(ItemRepository):
    # data = {
    #     "id": 1001,
    #     "name": "geek",
    #     "passion": "coding",
    # }
    
    # response = requests.post(url, json=data)
    # response = requests.get(url)
    
    # print("Status Code", response.status_code)
    # print("JSON Response ", response.json())


    def __init__(self, items_server_base_connection_url: str) -> None:
        super().__init__()
        self._base_url = items_server_base_connection_url # e.g. "http://item-service:8088/"
        self._item_details : Dict[str,Dict[str,float]] = dict() # item_id -> Dict

    def get_items(self, item_ids: List[str]) -> List[Item]:
        collected_items : List[Item] = []
        for item_id in item_ids:
            get_item_url = self._base_url + f"item/{item_id}" # e.g. "http://item-service:8088/" + "item/021309410341304fv9jsa0ivjcew"
            response = requests.get(get_item_url)
            print("[HTTPProxyItemRepository] sending HTTP GET request to items for item_id=",item_id)
            print(f"got status_code={response.status_code}")
            print(f"json response:\n {response.json()}")
            if response.status_code == 200:
                # {
                #     "id": "012f81ca-307c-463c-bfa3-d3da20c557d9",
                #     "userId": "96ff7d64-94fd-4a81-8ee0-37b4f403c21d",
                #     "description": "pedfdfsdcil",
                #     "quantity": 1,
                #     "price": 1.0,
                #     "shippingCosts": 1.0,
                #     "startTime": "2022-12-01 15:00:00.000000",
                #     "endTime": "2022-12-01 15:30:00.000000",
                #     "buyNow": false,
                #     "upForAuction": true,
                #     "counterfeit": false,
                #     "inappropriate": false,
                #     "categories": [],
                #     "bookmarks": []
                # }
                item = self._interpret_response(response.json())
                collected_items.append(item)
            else:
                # {'timestamp': '2022-11-28T14:51:59.567+00:00', 'status': 400, 'error': 'Bad Request', 'path': '/item/012f81ca-307c-463c-d3da20c557d9'}
                continue
        return collected_items

    def _interpret_response(self, json_data : Dict) -> Item:
        item_id = json_data["id"] if "id" in json_data else None
        userId = json_data["userId"] if "userId" in json_data else None
        description = json_data["description"] if "description" in json_data else None
        quantity = json_data["quantity"] if "quantity" in json_data else None
        price = json_data["price"] if "price" in json_data else None # in dollars (double type)
        shippingCosts = json_data["shippingCosts"] if "shippingCosts" in json_data else None # in dollars (double type)
        buyNow = json_data["buyNow"] if "buyNow" in json_data else None
        upForAuction = json_data["upForAuction"] if "upForAuction" in json_data else None
        counterfeit = json_data["counterfeit"] if "counterfeit" in json_data else None
        inappropriate = json_data["inappropriate"] if "inappropriate" in json_data else None
        print("item_id=",type(item_id),item_id) # str
        print("buyNow=",type(buyNow),buyNow) # bool
        print("price=",type(price),price) # float

        price_cents = int(price*100)
        shippingCosts_cents = int(shippingCosts*100)
        return Item(item_id,price_cents,shippingCosts_cents)

    def add_items(self, items: List[Item]) -> None:
        """helper method for debugging"""
        print("not saving item details because items gives me item details")


class InMemoryItemRepository(ItemRepository):

    def __init__(self) -> None:
        super().__init__()
        self._item_details : Dict[str,Dict[str,float]] = dict() # item_id -> Dict

    def get_items(self, item_ids: List[str]) -> List[Item]:
        items: List[Item] = []
        for item_id in self._item_details.keys():
            if item_id in set(item_ids):
                data = self._item_details
                item = self.to_item(data)
                items.append(item)
        return items

    def add_items(self, items: List[Item]) -> None:
        """helper method for debugging"""
        data = dict()
        for item in items:
            item_data = dict()
            item_data["item_id"] = item.item_id
            item_data["price_cents"] = item._price_cents
            item_data["shipping_cost_cents"] = item._shipping_cost_cents
            data[item.item_id] = item_data

    def to_item(self, data : Dict) -> Item:
        # {
        #     "item_id" : ,
        #     "price_cents" : ,
        #     "shipping_cost_cents" : ,
        # }
        return Item(data["item_id"],data["price_cents"],data["shipping_cost_cents"])
        
# class StubbedInMemoryItemRepository(ItemRepository):

#     def __init__(self) -> None:
#         super().__init__()
#         self._item_ids : Set[str] = set()

#     def get_items(self, item_ids: List[str]) -> List[Item]:
#         items: List[Item] = []
#         for item_id in self._item_details.keys():
#             if item_id in set(item_ids):
#                 data = self._item_details
#                 item = self.to_item(data)
#                 items.append(item)
#         return items

#     def add_items(self, items: List[Item]) -> None:
#         """helper method for debugging"""
#         data = dict()
#         for item in items:
#             item_data = dict()
#             item_data["item_id"] = item.item_id
#             item_data["price_cents"] = random.randint(50, 6000) # cents
#             item_data["shipping_cost_cents"] = shipping_cost = random.randint(300, 1000)
#             data[item.item_id] = item_data

#     def to_item(self, data : Dict) -> Item:
#         # {
#         #     "item_id" : ,
#         #     "price_cents" : ,
#         #     "shipping_cost_cents" : ,
#         # }
#         return Item(data["item_id"],data["price_cents"],data["shipping_cost_cents"]) 
