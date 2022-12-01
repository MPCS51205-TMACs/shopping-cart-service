from typing import Any, Dict, List, Optional, Tuple
import datetime
from fastapi.responses import HTMLResponse
import domain.utils as utils

from domain.cart_repository import CartRepository
from domain.receipt_repository import ReceiptRepository
from domain.bought_items_repository import BoughtItemsRepository
from domain.item_repository import ItemRepository
from domain.cart import Cart, Receipt, to_fancy_dollars
from domain.proxy_user_service import ProxyUserService
from domain.proxy_auctions_service import ProxyAuctionService

class CartService():

    def __init__(self,
        cart_repository : CartRepository,
        receipt_repository: ReceiptRepository,
        bought_items_repository: BoughtItemsRepository,
        item_repository: ItemRepository,
        proxy_user_service: ProxyUserService,
        proxy_auction_service: ProxyAuctionService) -> None:
        
        self._cart_repo = cart_repository
        self._receipt_repo = receipt_repository
        self._bought_items_repo = bought_items_repository
        self._item_repo = item_repository
        self._proxy_user_service = proxy_user_service
        self._proxy_auction_service = proxy_auction_service
        
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

        items_found = self._item_repo.get_items([item_id]) # expensive; synchronous HTTP request call in production
        if len(items_found) == 0:
            print("see cart_service.py full_checkout(). couldn't find item in item repository (items-context unaware of item or request to get item failed)!")
            print("aborting")
            return

        if len(items_found) != 1:
            print("see cart_service.py full_checkout(). unexpected case where we found 2 or more items in item repository with same item_id")
            print("aborting")
            return

        item_to_buy = items_found[0]
        item_to_buy._price_cents = price_cents # manually changing this items price because its resultant price is determined by auction result

        # his_cart = self._cart_repo.get_cart(user_id)
        # his_items = his_cart.empty()
        # his_cart.add(item_to_buy)
        # his_receipt = his_cart.checkout()
        paymentinfo = self._proxy_user_service.fetch_payment_info(user_id)
        if not paymentinfo:
            print("see cart_service.py full_checkout(). failed to find user payment info!")
            print("aborting")
            return

        his_receipt = Cart(user_id,[item_to_buy]).checkout(paymentinfo)
        print("\n"+his_receipt.to_console_str())

        # self._cart_repo.save_cart(his_cart)
        self._receipt_repo.save(his_receipt) # save receipt of the purchase
        self._bought_items_repo.add(item_id,his_receipt._receipt_id) # note to self: this item was bought
        

    def checkout(self, user_id:str) -> Tuple[List[str], List[str], Optional[Receipt]]:
        """
        executes a checkout; returns a list of violating item_ids of two kinds (items with
        live, ongoing auctions that cannot be bought, and items that have already been bought);
        also returns a receipt (in case of success);
        if checkout successful, will return two empty lists and a Receipt object;
        if checkout unsuccessful, will return two lists (at least one is non-empty) and None
        """
        print(f"[CartService] checking out cart of user_id={utils.short_str(user_id)}")

        # item_to_buy = self._item_repo.get_items([item_id]) # expensive; synchronous HTTP request call in production

        # TODO: replace below implementation with newly created endpoint that gives all item details given
        # set of item_ids; this allows us to get all details in one request--rather than send 1x request per item in cart
        his_cart = self._cart_repo.get_cart(user_id) # expensive; 1x synchronous HTTP request call in production for each item in cart

        paymentinfo = self._proxy_user_service.fetch_payment_info(user_id) # 1 synchronous HTTP request call in production
        if not paymentinfo:
            print("see cart_service.py full_checkout(). failed to find user payment info!. user may not exist or this service's auth token invalid")
            print("aborting")
            return

        his_receipt = his_cart.checkout(paymentinfo)
        his_items_purchased = his_cart.empty()

        # validate
        already_bought = 0
        already_bought_ids : List[str] = []
        already_live = 0
        already_live_ids : List[str] = []
        fail = False
        for item in his_items_purchased:
            if self._bought_items_repo.has(item.item_id): # check for violations: already purchased items
                already_bought+=1
                already_bought_ids.append(item.item_id)
            elif not item.is_pre_auction(utils.localize(datetime.datetime.now())): # check for violations: items with live auctions.
                already_live+=1
                already_live_ids.append(item.item_id)
        print("number of violations =", (already_bought + already_live))
        if already_bought > 0 or already_live > 0:
            fail = True
        
        if fail:
            if already_bought > 0:
                bought_items_str = ", ".join([utils.short_str(item_id) for item_id in already_bought_ids])
                print(f"[CartService] fail. {already_bought} item(s) have already been purchased: item_ids={bought_items_str}")
            if already_live > 0 :
                live_items_str = ", ".join([utils.short_str(item_id) for item_id in already_live_ids])
                print(f"[CartService] fail. {already_live} item(s) have live auctions: item_ids={live_items_str}")
            return already_bought_ids,already_live_ids, None
            # raise NotImplementedError("TO RETURN STATEMENT")
        else: # good to buy; BUT NEED TO CANCEL THE AUCTION
            for item in his_items_purchased:
                canceled = self._proxy_auction_service.stop_auction(item.item_id) # all should pass since they are just prior or at auction start
                if canceled:
                    print(f"[CartService] successfully instructed AuctionService to cancel auction for item_ids = {utils.short_str(item.item_id)}")
                else :
                    print(f"[CartService] Fail. Oh no! did NOT successfully instruct AuctionService to cancel auction for item_ids = {utils.short_str(item.item_id)}")
            for item in his_items_purchased: # note to self: these items are marked bought
                self._bought_items_repo.add(item.item_id,his_receipt._receipt_id)
            self._cart_repo.save_cart(his_cart) # save knowledge his cart is now empty
            self._receipt_repo.save(his_receipt) # save receipt of the purchase
            print(f"[CartService] success. purchase complete. {to_fancy_dollars(his_receipt._bill.total_cost())} charged to user_id={utils.short_str(user_id)}")
            return [],[],his_receipt
            # raise NotImplementedError("TO RETURN STATEMENT")

    def get_cart(self, user_id:str) -> Dict:
        print("[ClosedAuctionMetricsService] getting cart details...")

        if user_id:
            cart = self._cart_repo.get_cart(user_id) # semi expensive: HTTP synch request to items context
            return cart.to_data_dict()
        else:
            return Cart("",[]).to_data_dict()

    def get_bought_item(self, bought_item_id: str) -> Optional[Dict[str,str]]:
        """
        
        """
        if bought_item_id:
            _, receipt_id = self._bought_items_repo.get(bought_item_id)
            if receipt_id:
                return {
                    "item_id" : bought_item_id,
                    "receipt_id" : receipt_id
                }
        return None

    def get_receipt(self, receipt_id: str) -> Optional[Dict[str,Any]]:
        """
        
        """
        if receipt_id:
            receipt = self._receipt_repo.get(receipt_id)
            if receipt:
                return receipt.to_full_data_dict()
            else:
                print(f"see cart_service.py get_receipt(); encountered strange case where receipt_id={utils.short_str(receipt_id)} exists \
                but could not find receipt in database (receipt doesn't exist)")
                return None
        else:
            print(f"did not find a receipt with receipt_id={receipt_id}")
            return None

    def get_receipts(self, bought_item_id: Optional[str]=None) -> Optional[Dict[str,Any]]:
        """
        """
        if bought_item_id:
            _, receipt_id = self._bought_items_repo.get(bought_item_id)
            if receipt_id:
                receipt = self._receipt_repo.get(receipt_id)
                if receipt:
                    return receipt.to_full_data_dict()
                else:
                    # return 404
                    print(f"see cart_service.py get_receipts(); encountered strange case where item_id={utils.short_str(bought_item_id)} was bought but \
                     the associated receipt_id={utils.short_str(receipt_id)} does not correspond to a receipt in database (receipt doesn't exist)")
                    return None
            else:
                # return 404
                print(f"did not find a receipt with item_id={receipt_id}")
                return None
        else:
            print("NOT IMPLEMENTED: RETURN ALL CARTS (PROBABLY SHOULD LIMIT)")
            return None

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
