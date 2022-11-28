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
from fastapi.responses import HTMLResponse
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
        # self.router.add_api_route(f"/carts/{item_id}/visualization", self.get_closed_auction_visualization, response_class=HTMLResponse,methods=["GET"])
        
    def index(self) -> dict:
        """Returns a default response when no endpoint is specified.

        Returns
        -------
        index : `dict` [`str`, `str`]
            Default response
        """
        return {"home": "route"}

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
        violating_item_ids, receipt = self.cart_service.checkout(user_id)
        if len(violating_item_ids) > 0:
            bought_items_str = ", ".join([short_str(item_id) for item_id in violating_item_ids])
            raise HTTPException(status_code=404, detail=f"fail. the following items have already been purchased: {bought_items_str}")
        return { "message": "success!", "receipt": receipt.to_data_dict()}



def start_receiving_rabbitmsgs(cart_service : CartService):
    try:
        receive_rabbitmq_msgs(cart_service)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

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

        if "Cancellation" in jsondata:
            print(" [x] Ignoring. this is a canceled / stopped auction.")
            return

        if "WinningBid" in jsondata["WinningBid"]:
            item_id = jsondata["item_id"]
            user_id = jsondata["bidder_user_id"]
            amount_in_cents = jsondata["amount_in_cents"]
            cart_service.full_checkout(user_id,item_id,amount_in_cents)
            return 
        
        print("[main] SEE receive_rabbitmq_msgs(). reached end of method without understanding situation")

    
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
#     # channel.basic_qos(prefetch_count=1)
#     # channel.basic_consume(queue='task_queue', on_message_callback=callback)
    channel.start_consuming()

def startupRESTAPI(app: FastAPI, port:int, log_level:str = "info"):
    uvicorn.run(host="0.0.0.0",app=app, port=port, log_level=log_level)
    # proc = Process(target=uvicorn.run,
    #                 args=(app,),
    #                 kwargs={
    #                     "host": "0.0.0.0", # e.g. "127.0.0.1",
    #                     "port": port,
    #                     "log_level": "info"},
    #                 daemon=True)
    # proc.start()

LOCAL_PORT = 10001 # port for this service (And its restful api)

def main():

    app = FastAPI()

    inMemory = True

    if inMemory: # use in memory repos
        from domain.cart_repository import CartRepository, InMemoryCartRepository
        from domain.receipt_repository import ReceiptRepository, InMemoryReceiptRepository, MongoDbReceiptRepository
        from domain.bought_items_repository import BoughtItemsRepository, InMemoryBoughtItemsRepository, MongoDbBoughtItemsRepository
        from domain.item_repository import ItemRepository, InMemoryItemRepository, HTTPProxyItemRepository
        from domain.cart_repository_composite import CompositeCartRepository, CartItemsRepository, InMemoryCartItemsRepository, MongoDbCartItemsRepository
        
        receipt_repo : ReceiptRepository = InMemoryReceiptRepository()
        # receipt_repo : ReceiptRepository = MongoDbReceiptRepository(hostname=, port=)

        bought_items_repo : BoughtItemsRepository = InMemoryBoughtItemsRepository()
        # bought_items_repo : BoughtItemsRepository = MongoDbBoughtItemsRepository(hostname=, port=)

        # items_repo : ItemRepository = InMemoryItemRepository()
        item_service_connection_url = "http://item-service:8088/"
        items_repo : ItemRepository = HTTPProxyItemRepository(item_service_connection_url)
        cart_items_repo : CartItemsRepository = InMemoryCartItemsRepository()
        cart_repo : CartRepository = CompositeCartRepository(items_repo,cart_items_repo)


        # cart_service = CartService(cart_repo,receipt_repo,bought_items_repo,items_repo)

        items = [rand_item() for _ in range (20)]
        person1 =  "harry"
        person2 =  "Matt"
        person3 =  "Sam"
        person4 =  "Patricia"
        cart1 = Cart(person1,items[0:4])
        cart2 = Cart(person2,items[4:10])
        cart3 = Cart(person3,items[10:15])
        cart4 = Cart(person4,items[15:21])
        carts = [cart1,cart2,cart3,cart4]

        items_repo.add_items(items)
        for cart in carts:
            cart_repo.save_cart(cart)

        print(items)
        print()
        print(carts)
        
        BaseManager.register('CartService', CartService)
        manager = BaseManager()
        manager.start()
        cart_service = manager.CartService(cart_repo,receipt_repo,bought_items_repo,items_repo)

        api = RESTAPI(cart_service)
        app.include_router(api.router)
        
        # spawn child process to handle the HTTP requests against the REST api
        startupRESTAPI(app,LOCAL_PORT)

        # main function enters method that blocks and never returns
        start_receiving_rabbitmsgs(cart_service)

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