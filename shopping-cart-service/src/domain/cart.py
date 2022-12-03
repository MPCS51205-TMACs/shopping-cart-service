from __future__ import annotations
import datetime
from typing import List, Dict
import uuid, random, string

from domain.utils import *

class Cart(object):

    def __init__( self, user_id : str, items : List[Item]) -> None:
        # 'user_id' is a 
        self._user_id = user_id
        self._items = items

    def total_cost(self) -> float:
        """returns total cost in cents"""
        return Bill(self._items).total_cost()

    def empty(self) -> List[Item]:
        """empties the cart (removes all items)"""
        his_items = self._items.copy()
        self._items : List[Item] = []
        return his_items

    def __repr__(self) -> str:
        args = f"user_id={short_str(self._user_id)}, "
        args += f"num_items=[{len(self._items)}], "
        args += f"tot_cost={to_fancy_dollars(self.total_cost())}"
        return "Cart(" + args + ")" 

    def add(self, item :Item) -> bool:
        """returns true if successfully added; returns false if already in cart"""
        if item.item_id in [item.item_id for item in self._items]:
            return False
        else:
            self._items.append(item)
            return True
    
    def remove(self,query_item_id :str) -> bool:
        """returns true if successfully removed; returns false if it wasn't in cart"""
        for item in self._items:
            if item.item_id == query_item_id:
                self._items.remove(item)
                return True
        return False

    def checkout(self, payment_info: str) -> Receipt:
        print(f"[Cart] checking out...using payment info: '{payment_info}'. generated receipt.")
        # TODO: get payment info
        return Receipt(str(uuid.uuid4()),Bill(self._items),localize(datetime.datetime.now()),payment_info, self._user_id)

    def __contains__(self, item_id: str):
        if item_id in [item.item_id for item in self._items]:
            return True 

    def to_data_dict(self) -> Dict:
        """
        returns a json-like representation of the internal contents
        of a Cart.
        """

        return {
            'user_id': self._user_id,
            'total_cost_cents': self.total_cost(),
            'items': [item.to_data_dict() for item in self._items],
        }

class Receipt(object):

    def __init__(self,  receipt_id: str, bill: Bill, time: datetime.datetime, payment_info : str, user_id : str) -> None:
        self._bill = bill
        self._receipt_id = receipt_id
        self._time = time
        self._payment_info = payment_info
        self._user_id = user_id

    def __repr__(self) -> str:
        args = ", ".join([short_str(self._receipt_id),to_fancy_dollars(self._bill.total_cost()), toSQLTimestamp6Repr(self._time)+" UTC"])
        return "Receipt[" + args + "]"

    def to_data_dict(self) -> Dict:
        """
        returns a json-like representation of the internal contents
        of a Receipt.
        """

        return {
            'receipt_id': self._receipt_id,
            'user_id': self._user_id,
            'time_processed': toSQLTimestamp6Repr(self._time),
            'bill': self._bill.to_data_dict(),
            'payment_info': self._payment_info
        }

    def to_full_data_dict(self) -> Dict:
        """
        returns a json-like representation of the internal contents
        of a Receipt.
        """

        return {
            'receipt_id': self._receipt_id,
            'user_id': self._user_id,
            'time_processed': toSQLTimestamp6Repr(self._time),
            'bill': self._bill.to_data_dict(),
            'payment_info': self._payment_info,
            'repr': self.to_console_str()
        }

    @staticmethod
    def from_data_dict_to_receipt(data: Dict) -> Receipt:
        """
        returns a Receipt from a json-like representation of the internal contents
        of a Receipt.
        """

        receipt_id = data["receipt_id"] if "receipt_id" in data else ""
        user_id = data["user_id"] if "user_id" in data else ""
        time_processed = toDatetimeFromStr(data["time_processed"]) if "time_processed" in data else None
        bill = Bill.from_data_dict_to_bill(data["bill"]) if "bill" in data else None
        payment_info = data["payment_info"] if "payment_info" in data else ""
        return Receipt(receipt_id,bill,time_processed,payment_info,user_id)

    def to_console_str(self) -> str:
        """returns a string representation of a receipt, with new line characters;
        meant to be a pretty representation when printing to console"""
        width = 58
        receipt_str = "#"*width
        receipt_str += f"\n# receipt_id: {(short_str(self._receipt_id,width-18)).rjust(width-16)} #"
        receipt_str += f"\n# user_id: {(short_str(self._receipt_id,width-21)).rjust(width-16)} #"
        receipt_str += f"\n# date: {(short_str(toSQLTimestamp6Repr(self._time),width-8)).rjust(width-16)} [UTC] #"
        receipt_str += f"\n# payment_info: {(short_str(self._payment_info,width-24)).rjust(width-18)} #"
        receipt_str += "\n#"+" "*(width-2)+"#"
        receipt_str += f"\n# item_ids"+" "*(width-19)+" price  #"
        receipt_str += "\n"+"#"*width
        for item in self._bill._items:
            line_item_width = width - 4
            amount_str = to_fancy_dollars(item.total_cost())
            amount_width = len(amount_str)
            space_for_user_id = line_item_width-amount_width-1
            user_id_repr = short_str(item.item_id,space_for_user_id)
            user_id_repr = user_id_repr.ljust(space_for_user_id)
            content = f"# {user_id_repr} {amount_str} #"
            receipt_str+="\n"+content
        receipt_str += "\n# "+" "*(width-13)+"-"*9+" #"
        receipt_str += "\n# "+to_fancy_dollars(self._bill.total_cost()).rjust(width-4)+" #"
        receipt_str += "\n"+"#"*width
        return receipt_str

    def _short_str(letters: str, limit : int = 6) -> str:
        return (letters[:limit] + '..') if len(letters) > limit else letters

class Bill(object):

    def __init__(self, items : List[Item]) -> None:
        self._items = items

    def total_cost(self) -> int:
        total = 0
        for item in self._items:
            total += item.total_cost()
        return total

    def __repr__(self) -> str:
        args = ",".join([short_str(str(item)) for item in self._items])
        return "Bill[" + args + "]" 

    def to_data_dict(self) -> Dict:
        """
        returns a json-like representation of the internal contents
        of a Bil.
        """

        return {
            'total_cost_str': to_fancy_dollars(self.total_cost()),
            'total_cost_cents': self.total_cost(),
            'items': [item.to_data_dict() for item in self._items],
        }

    @staticmethod
    def from_data_dict_to_bill(data) -> Dict:
        """
        returns a Bill from json-like representation of the internal contents
        of a Bill.
        """
        items = [Item.from_data_dict_to_bill(item_data) for item_data in data["items"]]
        return Bill(items)

class Item(object):

    def __init__(self, item_id : str, price_cents : int,  shipping_cost_cents : int, auction_start_time : datetime.datetime, buy_now: bool, counterfeit: bool, inappropriate: bool  ) -> None:
        self.item_id = item_id
        self._price_cents = price_cents
        self._shipping_cost_cents = shipping_cost_cents
        self._auction_start_time = auction_start_time
        self._buy_now = buy_now
        self._counterfeit = counterfeit
        self._inappropriate = inappropriate

    def total_cost(self) -> int:
        return self._price_cents + self._shipping_cost_cents

    def price(self) -> int:
        """in cents (USD)"""
        return self._price_cents
    
    def shipping_cost(self) -> int:
        """in cents (USD)"""
        return self._shipping_cost_cents

    def is_pre_auction(self, aDatetime: datetime.datetime) -> bool:
        return aDatetime < self._auction_start_time

    def __repr__(self) -> str:
        args = f"{short_str(self.item_id)}"
        return "Item(" + args + ")"

    def is_buynow_activatiated(self) -> bool:
        return self._buy_now

    def is_counterfeit(self) -> bool:
        return self._counterfeit

    def is_inappropriate(self) -> bool:
        return self._inappropriate

    def to_data_dict(self) -> Dict:
        """
        returns a json-like representation of the internal contents
        of an Item.
        """

        return {
            'item_id': self.item_id,
            'price_cents': self.price(),
            'shipping_cost_cents': self.shipping_cost(),
            'auction_start_time': self._auction_start_time, # datetime
            'buy_now': self._buy_now, # datetime
            'counterfeit': self._counterfeit,
            'inappropriate': self._inappropriate
        }

    @staticmethod
    def from_data_dict_to_bill(data) -> Bill:
        return Item(data['item_id'],data['price_cents'],data['shipping_cost_cents'],data['auction_start_time'],data['buy_now'],data['counterfeit'],data['inappropriate'])

def rand_items(quantity: int = 5) -> List[Item]:
    return [rand_item() for _ in range(quantity)]

def rand_item() -> Item:
    item_id = str(uuid.uuid4())
    cents = random.randint(50, 6000) # cents
    shipping_cost = random.randint(300, 1000)
    item = Item(item_id,cents,shipping_cost,datetime.datetime.now(), True,False,False)
    return item

def rand_cart() -> Cart:
    rand_name = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    return Cart(rand_name, rand_items())

def rand_carts(quantity: int = 5) -> List[Cart]:
    return [rand_cart() for _ in range(quantity)]

if __name__ == "__main__":
    print(rand_item())
    print(rand_items())
    
    items = rand_items()
    bill = Bill(items)

    print(bill)
    print(bill.total_cost())
    print(to_fancy_dollars(bill.total_cost()))

    cart = Cart("alex", rand_items())
    print(cart)
    print(cart.total_cost())

    print("bobbypin" in cart)
    item = Item("bobbypin",3000,2000, datetime.datetime.now(),True,False,False)
    cart.add(item)
    print("bobbypin" in cart)
    cart.remove(item.item_id)
    print("bobbypin" in cart)
    receipt = cart.checkout("asdfj;l1k3241-9u1f3kfj3as") # random payment info
    print(receipt)
    print()
    print(cart.to_data_dict())
