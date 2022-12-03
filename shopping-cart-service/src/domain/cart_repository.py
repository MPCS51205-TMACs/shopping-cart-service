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