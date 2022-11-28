from typing import Dict, List, Optional, Tuple
import datetime
from fastapi.responses import HTMLResponse
import domain.utils as utils

from domain.cart_repository import CartRepository
from domain.receipt_repository import ReceiptRepository
from domain.bought_items_repository import BoughtItemsRepository
from domain.item_repository import ItemRepository
from domain.cart import Cart, Receipt, to_fancy_dollars

class CartService():

    def __init__(self,
        cart_repository : CartRepository,
        receipt_repository: ReceiptRepository,
        bought_items_repository: BoughtItemsRepository,
        item_repository: ItemRepository) -> None:
        
        self._cart_repo = cart_repository
        self._receipt_repo = receipt_repository
        self._bought_items_repo = bought_items_repository
        self._item_repo = item_repository
        
    def add_item_to_cart(self, user_id: str, item_id: str) -> bool:
        print("[CartService] adding item to cart")
        his_cart = self._cart_repo.get_cart(user_id)
        items_found = self._item_repo.get_items([item_id])
        if len(items_found) != 1:
            print("[CartService] fail. could not find item.")
            return False
        else:
            item = items_found[0]
            newly_added = his_cart.add(item) # added if wasn't already in there
            if not newly_added:
                print("[CartService] success (trivial). item was already in cart.")
            self._cart_repo.save_cart(his_cart)
            return True # make operation idempotent
        
    def remove_item_from_cart(self, user_id: str, item_id:str) -> bool:
        print(f"[CartService] removing item_id={utils.short_str(item_id)} from cart of user_id={utils.short_str(user_id)} [STUBBED]")
        his_cart = self._cart_repo.get_cart(user_id)
        removed = his_cart.remove(item_id) # true if was already in there
        self._cart_repo.save_cart(his_cart)
        return removed

    def full_checkout(self, user_id: str, item_id: str, price_cents: int):
        print(f"[CartService] doing full checkout: user_id={utils.short_str(user_id)} buys item_id={utils.short_str(item_id)} [STUBBED]")
        
        if self._bought_items_repo.has(item_id): # was this item already bought?
            print(f"[CartService] fail. this item was already purchased.")
            return

        item_to_buy = self._item_repo.get_items([item_id]) # expensive; synchronous HTTP request call in production
        # his_cart = self._cart_repo.get_cart(user_id)
        # his_items = his_cart.empty()
        # his_cart.add(item_to_buy)
        # his_receipt = his_cart.checkout()
        his_receipt = Cart(user_id,[item_to_buy]).checkout()

        # self._cart_repo.save_cart(his_cart)
        self._receipt_repo.save(his_receipt) # save receipt of the purchase
        self._bought_items_repo.add(item_id) # note to self: this item was bought
        

    def checkout(self, user_id:str) -> Tuple[List[str], Optional[Receipt]]:
        """
        executes a checkout and returns a list of violating item_ids; i.e., item_ids
        corresponding to items already bought; len(item_ids)==0 indicates success; failure
        if len != 0
        """
        print(f"[CartService] checking out cart of user_id={utils.short_str(user_id)}")

        # item_to_buy = self._item_repo.get_items([item_id]) # expensive; synchronous HTTP request call in production

        his_cart = self._cart_repo.get_cart(user_id) # expensive; synchronous HTTP request call in production
        his_receipt = his_cart.checkout()
        his_items_purchased = his_cart.empty()

        # validate
        already_bought = 0
        already_bought_ids : List[str] = []
        for item in his_items_purchased:
            if self._bought_items_repo.has(item.item_id):
                already_bought+=1
                already_bought_ids.append(item.item_id)
        if already_bought > 0:
            bought_items_str = ", ".join([utils.short_str(item_id) for item_id in already_bought_ids])
            print(f"[CartService] fail. {already_bought} of items have already been purchased: purchased item_ids={bought_items_str}")
            return already_bought_ids, None
            # raise NotImplementedError("TO RETURN STATEMENT")
        else: # good to buy
            for item in his_items_purchased: # note to self: these items are marked bought
                self._bought_items_repo.add(item.item_id)
            self._cart_repo.save_cart(his_cart) # save knowledge his cart is now empty
            self._receipt_repo.save(his_receipt) # save receipt of the purchase
            print(f"[CartService] success. purchase complete. {to_fancy_dollars(his_receipt._bill.total_cost())} charged to user_id={utils.short_str(user_id)}")
            return [],his_receipt
            # raise NotImplementedError("TO RETURN STATEMENT")

    def get_cart(self, user_id:str) -> Dict:
        print("[ClosedAuctionMetricsService] getting cart details...")

        if user_id:
            cart = self._cart_repo.get_cart(user_id) # semi expensive: HTTP synch request to items context
            return cart.to_data_dict()
        else:
            return Cart("",[]).to_data_dict()

    # def convert_to_dict(self) -> Dict:
    #     """
    #     returns a json-like representation of the internal contents
    #     of a ClosedAuction.
    #     """

    #     return {
    #         'item_id': self._item_id,
    #         'start_price_in_cents': self._start_price_in_cents,
    #         'start_time': utils.toSQLTimestamp6Repr(self._start_time),
    #         'end_time': utils.toSQLTimestamp6Repr(self._end_time),
    #         'cancellation_time': utils.toSQLTimestamp6Repr(self._cancellation_time) if self._cancellation_time else "",
    #         'finalized_time': utils.toSQLTimestamp6Repr(self._finalized_time),
    #         'bids': [bid.convert_to_dict() for bid in self._bids],
    #         'winning_bid': self._winning_bid.convert_to_dict() if self._winning_bid else None,
    #     }
