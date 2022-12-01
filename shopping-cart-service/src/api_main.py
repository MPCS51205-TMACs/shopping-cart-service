"""This module acts as the API for microservice. Implements the FastAPI package."""

import datetime
import json
from typing import Optional, Union, Dict
from fastapi import FastAPI, Header, HTTPException, APIRouter
from application.requests_responses import *
import uvicorn
# from application.closed_auction_metrics_service import ClosedAuctionMetricsService
# from domain.auction_repository import AuctionRepository, InMemoryAuctionRepository
# from domain.auction_repository_mongo import MongoDbAuctionRepository
import asyncio
import pika, sys, os
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
# from infrastructure import utils
# from domain.bid import Bid
# from domain.closed_auction import ClosedAuction
from fastapi.responses import HTMLResponse, JSONResponse
import pprint
from domain.cart_service import CartService
from domain.cart import rand_carts, rand_items, rand_item, rand_cart, Cart
from domain.utils import *

VERSION = 'v1'

class RequestAddItem(BaseModel):
    user_id: str
    item_id: str

class RequestRemoveItem(BaseModel):
    user_id: str
    item_id: str

class RequestCheckout(BaseModel):
    user_id: str

class RESTAPI:

    def __init__(self, cart_service: CartService):
        self.cart_service = cart_service
        self.router = APIRouter()
        # self.router.add_api_route("/hello", self.hello, methods=["GET"])
        self.router.add_api_route("/", self.index, methods=["GET"])
        self.router.add_api_route("/carts/{user_id}", self.get_cart, methods=["GET"])
        self.router.add_api_route("/carts/item", self.add_item_to_cart, methods=["POST"])
        self.router.add_api_route("/carts/item", self.remove_item_from_cart, methods=["DELETE"])
        self.router.add_api_route("/carts/checkout", self.checkout, methods=["POST"])
        self.router.add_api_route("/boughtitems/{bought_item_id}", self.get_bought_item, methods=["GET"])
        self.router.add_api_route("/receipts/{receipt_id}", self.get_receipt, methods=["GET"])
        self.router.add_api_route("/receipts/", self.get_receipts, methods=["GET"]) # expect query parameter for item_id

        # self.router.add_api_route(f"/carts/{item_id}/visualization", self.get_closed_auction_visualization, response_class=HTMLResponse,methods=["GET"])
        
    def index(self) -> dict:
        """Returns a default response when no endpoint is specified.

        Returns
        -------
        index : `dict` [`str`, `str`]
            Default response
        """
        return {"home": "route"}

    def get_bought_item(self, bought_item_id: str) -> Dict:
        """
        
        """
        # pass
        # always returns a 200
        return self.cart_service.get_bought_item(bought_item_id)

    def get_receipt(self, receipt_id: str) -> Dict:
        """
        
        """
        # pass
        # always returns a 200
        return self.cart_service.get_receipt(receipt_id)

    def get_receipts(self, item_id: Optional[str]=None, user_id: Optional[str]=None) -> Dict:
        """
        NOTE for now, always expecting a query parameter with an item_id or user_id
        """
        # pass
        # always returns a 200
        return self.cart_service.get_receipts(bought_item_id=item_id, user_id=user_id)

    def get_cart(self, user_id: str) -> Dict:
        """
        Returns a response containing cart information.

        Parameters
        ----------
        user_id : `str`
            UUID of the user

        Returns
        -------
        : `dict` [`str`, `dict`]
            A response keyed by item_id where each key is mapped to a 
            dictionary containing information about the cart.
        
        Notes
        -----

        Sample URLs
        
        Sample response body:
        {        }
        """
        # always returns a 200
        return self.cart_service.get_cart(user_id)

    def add_item_to_cart(self, request_body: RequestAddItem):
        """
        can fail if: can't find in item repository;
        else, succeeds
        """
        item_id = request_body.item_id
        user_id = request_body.user_id
        added = self.cart_service.add_item_to_cart(user_id,item_id)
        if not added:
            raise HTTPException(status_code=404, detail=f"could not find item_id={item_id}")
        return { "message": f"success! added item_id={short_str(item_id)} to cart of user_id={user_id}"}

    def remove_item_from_cart(self, request_body: RequestRemoveItem):
        """
        can fail if: can't find item in cart;
        else, succeeds
        """
        item_id = request_body.item_id
        user_id = request_body.user_id
        removed = self.cart_service.remove_item_from_cart(user_id,item_id)
        if not removed:
            raise HTTPException(status_code=400, detail=f"item_id={short_str(item_id)} was not in cart of user_id={user_id}")
        return { "message": f"success! removed item_id={short_str(item_id)} from cart of  user_id={user_id}"}

    def checkout(self, request_body : RequestCheckout):
        """
        fails if an item in the cart is already purchased;
        else, succeeds
        """
        user_id = request_body.user_id
        already_bought_item_ids, item_ids_w_live_auctions, receipt = self.cart_service.checkout(user_id)
        # add case for items not existing / not being able to find the item (i.e. items context doesn't have the item details)??
        if len(already_bought_item_ids) + len(item_ids_w_live_auctions) > 0:
            bought_items_str = ", ".join([short_str(item_id) for item_id in already_bought_item_ids])
            live_items_str = ", ".join([short_str(item_id) for item_id in item_ids_w_live_auctions])
            msg = "fail."
            msg += ("Cart contained items that were already bought: "+ bought_items_str) if len(already_bought_item_ids) > 0 else ""
            msg += ("Cart contained items with live auctions: "+ live_items_str) if len(item_ids_w_live_auctions) > 0 else ""
            return JSONResponse(
                status_code=400,
                content={
                    "message": msg,
                    "already_bought_item_ids": already_bought_item_ids,
                    "live_item_ids": item_ids_w_live_auctions
                }
            )
        if receipt:
            print(receipt.to_console_str())
        return { "message": "success!", "receipt": receipt.to_data_dict()}



def start_receiving_rabbitmsgs(cart_service : CartService):
    # try:
        receive_rabbitmq_msgs(cart_service)
    # except KeyboardInterrupt:
    #     print('Interrupted')
    #     try:
    #         sys.exit(0)
    #     except SystemExit:
    #         os._exit(0)

def receive_rabbitmq_msgs(cart_service : CartService):

    RABBITMQ_HOST = "rabbitmq-server" # e.g. "localhost"
    EXCHANGE_NAME = "auction.end"
    QUEUE_NAME = "cart.consume-auctionend"

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout', durable=True)
    result = channel.queue_declare(queue=QUEUE_NAME, durable=True) #durable=True exclusive=False,
    queue_name = result.method.queue

    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name)
    
    print(' [*] [handle auction.end] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(" [x] received new auction data.")
        jsondata = json.loads(body)
        print(json.dumps(jsondata, indent=2))

        if "Cancellation" in jsondata and jsondata["Cancellation"] is not None:
            print("[main] ignoring. this was a cancelled auction.")
            return

        if "WinningBid" in jsondata and jsondata["WinningBid"] is not None:
            item_id = jsondata["WinningBid"]["item_id"]
            user_id = jsondata["WinningBid"]["bidder_user_id"]
            amount_in_cents = jsondata["WinningBid"]["amount_in_cents"]
            cart_service.full_checkout(user_id,item_id,amount_in_cents)
            return 

        if "Bids" in jsondata and len(jsondata["Bids"]) == 0:
            print("[main] ignoring. no winner, no cancellation.")
            return
        
        print("[main] SEE receive_rabbitmq_msgs(). reached end of method without understanding situation")

    
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
#     # channel.basic_qos(prefetch_count=1)
#     # channel.basic_consume(queue='task_queue', on_message_callback=callback)
    channel.start_consuming()

def startupRESTAPI(app: FastAPI, port:int, log_level:str = "info"):
    # uvicorn.run(host="0.0.0.0",app=app, port=port, log_level=log_level)
    proc = Process(target=uvicorn.run,
                    args=(app,),
                    kwargs={
                        "host": "0.0.0.0", # e.g. "127.0.0.1",
                        "port": port,
                        "log_level": "info"},
                    daemon=True)
    proc.start()

LOCAL_PORT = 10001 # port for this service (And its restful api)

def main():

    app = FastAPI()

    inMemory = False

    from domain.cart_repository import CartRepository, InMemoryCartRepository
    from domain.receipt_repository import ReceiptRepository, InMemoryReceiptRepository, MongoDbReceiptRepository
    from domain.bought_items_repository import BoughtItemsRepository, InMemoryBoughtItemsRepository, MongoDbBoughtItemsRepository
    from domain.item_repository import ItemRepository, InMemoryItemRepository, HTTPProxyItemRepository
    from domain.cart_repository_composite import CompositeCartRepository, CartItemsRepository, InMemoryCartItemsRepository, MongoDbCartItemsRepository
    from domain.proxy_user_service import ProxyUserService, StubbedProxyUserService, HTTPProxyUserService
    from domain.proxy_auctions_service import ProxyAuctionService, StubbedProxyAuctionService, HTTPProxyAuctionService
    
    mongo_hostname = "cart-mongo-server"
    mongo_port = "27017" # e.g. 27017
    # base connection url = mongodb://{hostname}:{port}/

    if inMemory:
        receipt_repo : ReceiptRepository = InMemoryReceiptRepository()
        bought_items_repo : BoughtItemsRepository = InMemoryBoughtItemsRepository()
        cart_items_repo : CartItemsRepository = InMemoryCartItemsRepository()
    else:
        receipt_repo : ReceiptRepository = MongoDbReceiptRepository(hostname=mongo_hostname, port=mongo_port)
        bought_items_repo : BoughtItemsRepository = MongoDbBoughtItemsRepository(hostname=mongo_hostname, port=mongo_port)
        cart_items_repo : CartItemsRepository = MongoDbCartItemsRepository(hostname=mongo_hostname, port=mongo_port)

    # TODO: for now, shoppingcart will use an admin token that lasts ~30 days from now (11/30/2022)
    # in future, this service needs to obtain an admin token it can use to ask User-service for admin-level
    # details on Users (payment info).
    TEMP_ADMIN_SERVICE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NDcwMTVjOC1kODI4LTQwNGUtYjg3OC1lYThlNTRhMzk5ZDkiLCJpc3MiOiJ1c2VyLXNlcnZpY2UiLCJhdWQiOiJtcGNzNTEyMDUiLCJlbWFpbCI6Im1hdHRAbXBjcy5jb20iLCJuYW1lIjoibWF0dCIsImF1dGhvcml0aWVzIjpbIlJPTEVfVVNFUiIsIlJPTEVfQURNSU4iXSwiaWF0IjoxNjY5NDA4MDY2LCJleHAiOjE2NzIwMDAwNjZ9.N1x3fIBUz9CLDtabc9Lig6a4VFmRPdQaJwYX2Vabov0"
    user_connection_url = "http://user-service:8080"
    proxy_user_service : ProxyUserService = HTTPProxyUserService(user_connection_url,TEMP_ADMIN_SERVICE_TOKEN)
    # proxy_user_service : ProxyUserService = StubbedProxyUserService()

    auction_connection_url = "http://auctions-service:10000"
    proxy_auction_service : ProxyAuctionService = HTTPProxyAuctionService(auction_connection_url,TEMP_ADMIN_SERVICE_TOKEN)

    # items_repo : ItemRepository = InMemoryItemRepository()
    item_service_connection_url = "http://item-service:8088/"
    items_repo : ItemRepository = HTTPProxyItemRepository(item_service_connection_url)
    cart_repo : CartRepository = CompositeCartRepository(items_repo,cart_items_repo)


    # cart_service = CartService(cart_repo,receipt_repo,bought_items_repo,items_repo)

    # items = [rand_item() for _ in range (20)]
    # person1 =  "harry"
    # person2 =  "Matt"
    # person3 =  "Sam"
    # person4 =  "Patricia"
    # cart1 = Cart(person1,items[0:4])
    # cart2 = Cart(person2,items[4:10])
    # cart3 = Cart(person3,items[10:15])
    # cart4 = Cart(person4,items[15:21])
    # carts = [cart1,cart2,cart3,cart4]

    # items_repo.add_items(items)
    # for cart in carts:
    #     cart_repo.save_cart(cart)

    # print(items)
    # print()
    # print(carts)
    
    if inMemory:
        BaseManager.register('CartService', CartService)
        manager = BaseManager()
        manager.start()
        cart_service = manager.CartService(cart_repo,receipt_repo,bought_items_repo,items_repo, proxy_user_service, proxy_auction_service)

        api = RESTAPI(cart_service)
        app.include_router(api.router)
        
        # spawn child process to handle the HTTP requests against the REST api
        startupRESTAPI(app,LOCAL_PORT)

        # main function enters method that blocks and never returns
        start_receiving_rabbitmsgs(cart_service)
    else:
        cart_service1 = CartService(cart_repo,receipt_repo,bought_items_repo,items_repo, proxy_user_service, proxy_auction_service)
        cart_service2 = CartService(cart_repo,receipt_repo,bought_items_repo,items_repo, proxy_user_service, proxy_auction_service)
        api = RESTAPI(cart_service1)
        app.include_router(api.router)
        
        # spawn child process to handle the HTTP requests against the REST api
        startupRESTAPI(app,LOCAL_PORT)

        # main function enters method that blocks and never returns
        start_receiving_rabbitmsgs(cart_service2)

        # auction_repo: AuctionRepository = InMemoryAuctionRepository()
        

        # bid1 = Bid.generate_basic_bid(100,200)
        # bid2 = Bid.generate_basic_bid(101,200)
        # bid3 = Bid.generate_basic_bid(102,200)
        # start = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=0, minute=0, second=0,microsecond=130002 ))
        # duration = datetime.timedelta(minutes=30)
        # auction1 = ClosedAuction.generate_auction([bid1,bid2,bid3],200, start, duration)

        # bid4 = Bid.generate_basic_bid(103,201)
        # bid5 = Bid.generate_basic_bid(104,201)
        # start2 = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=1, minute=10, second=0,microsecond=130002 ))
        # duration2 = datetime.timedelta(minutes=24)
        # auction2 = ClosedAuction.generate_auction([bid4,bid5],201, start2, duration2)

        # bid6 = Bid.generate_basic_bid(105,202)
        # start3 = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=1, minute=17, second=10,microsecond=130002 ))
        # duration3 = datetime.timedelta(minutes=14)
        # auction3 = ClosedAuction.generate_auction([bid6],202, start3,duration)

        # auction_repo.save_auction(auction1)
        # auction_repo.save_auction(auction2)
        # auction_repo.save_auction(auction3)
    
        # app.closed_auction_metrics_service = closed_auction_metrics_service.ClosedAuctionMetricsService(auction_repo)
        # cart_service = ClosedAuctionMetricsService(auction_repo)


    #     BaseManager.register('ClosedAuctionMetricsService', ClosedAuctionMetricsService)
    #     manager = BaseManager()
    #     manager.start()
    #     cart_service = manager.ClosedAuctionMetricsService(auction_repo)
    
    #     api = RESTAPI(cart_service)
    #     app.include_router(api.router)
        
    #     # spawn child process to handle the HTTP requests against the REST api
    #     startupRESTAPI(app,LOCAL_PORT)

        # # main function enters method that blocks and never returns
        # start_receiving_rabbitmsgs(cart_service)
    # else: # use sql repos
    #     # auction_repo: AuctionRepository = InMemoryAuctionRepository()
    #     CAM_MONGO_CONTAINER_HOSTNAME = "cam-mongo-server"
    #     auction_repo1: AuctionRepository = MongoDbAuctionRepository(CAM_MONGO_CONTAINER_HOSTNAME)
    #     auction_repo2: AuctionRepository = MongoDbAuctionRepository(CAM_MONGO_CONTAINER_HOSTNAME)

    #     # bid1 = Bid.generate_basic_bid(100,200)
    #     # bid2 = Bid.generate_basic_bid(101,200)
    #     # bid3 = Bid.generate_basic_bid(102,200)
    #     # start = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=0, minute=0, second=0,microsecond=130002 ))
    #     # duration = datetime.timedelta(minutes=30)
    #     # auction1 = ClosedAuction.generate_auction([bid1,bid2,bid3],200, start, duration)

    #     # bid4 = Bid.generate_basic_bid(103,201)
    #     # bid5 = Bid.generate_basic_bid(104,201)
    #     # start2 = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=1, minute=10, second=0,microsecond=130002 ))
    #     # duration2 = datetime.timedelta(minutes=24)
    #     # auction2 = ClosedAuction.generate_auction([bid4,bid5],201, start2, duration2)

    #     # bid6 = Bid.generate_basic_bid(105,202)
    #     # start3 = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=1, minute=17, second=10,microsecond=130002 ))
    #     # duration3 = datetime.timedelta(minutes=14)
    #     # auction3 = ClosedAuction.generate_auction([bid6],202, start3,duration)

    #     # auction_repo2.save_auction(auction1)
    #     # auction_repo2.save_auction(auction2)
    #     # auction_repo2.save_auction(auction3)

    #     cart_service1 = ClosedAuctionMetricsService(auction_repo1)
    #     cart_service2 = ClosedAuctionMetricsService(auction_repo2)

    #     api = RESTAPI(cart_service1)
    #     app.include_router(api.router)
        
    #     # spawn child process to handle the HTTP requests against the REST api
    #     startupRESTAPI(app,LOCAL_PORT)

    #     # main function enters method that blocks and never returns
    #     start_receiving_rabbitmsgs(cart_service2)

if __name__ == "__main__":
    main()