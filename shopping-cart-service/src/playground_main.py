# from typing import Optional, Union, Dict

# from application.closed_auction_metrics_service import ClosedAuctionMetricsService
# from domain.auction_repository import AuctionRepository, InMemoryAuctionRepository
# from domain.auction_repository_mongo import MongoDbAuctionRepository
# from infrastructure import utils
# from domain.bid import Bid
# from domain.closed_auction import ClosedAuction

from domain.cart import *

# import datetime
import requests
from domain.item_repository import HTTPProxyItemRepository
from domain.proxy_user_service import ProxyUserService, StubbedProxyUserService, HTTPProxyUserService
from domain.proxy_auctions_service import ProxyAuctionService, HTTPProxyAuctionService
from domain.receipt_repository import *

def main():
    # item_id = "012f81ca-307c-463c-d3da20c557d9"
    url = "http://item-service:8088"
    TEMP_ADMIN_SERVICE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NDcwMTVjOC1kODI4LTQwNGUtYjg3OC1lYThlNTRhMzk5ZDkiLCJpc3MiOiJ1c2VyLXNlcnZpY2UiLCJhdWQiOiJtcGNzNTEyMDUiLCJlbWFpbCI6Im1hdHRAbXBjcy5jb20iLCJuYW1lIjoibWF0dCIsImF1dGhvcml0aWVzIjpbIlJPTEVfVVNFUiIsIlJPTEVfQURNSU4iXSwiaWF0IjoxNjY5NDA4MDY2LCJleHAiOjE2NzIwMDAwNjZ9.N1x3fIBUz9CLDtabc9Lig6a4VFmRPdQaJwYX2Vabov0"
    temp="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIwYTQ3ZjUzMy03YzMxLTQ4NTYtOTEzOS1iZTE5OGE1MWEwYTgiLCJhdWQiOiJtcGNzNTEyMDUiLCJyZXZvY2F0aW9uSWQiOiIyOGI0ZmUyOC00NTJjLTQ2MDMtOWY0NC0xY2QyMjk1MDE2N2QiLCJpc3MiOiJ1c2VyLXNlcnZpY2UiLCJuYW1lIjoiWFNzYndMZGRYdGJHaDVzIiwiZXhwIjoxNjcwMTc5MzE1LCJpYXQiOjE2NzAxMzYxMTUsImVtYWlsIjoiWFNzYndMZGRYdGJHaDVzQG1wY3MuY29tIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9VU0VSIiwiUk9MRV9BRE1JTiJdfQ.wNHzDx2WElch5EXmPLDkc-BMDIxxsQaYEmRqdRJmzjA"
    proxy = HTTPProxyItemRepository(url, temp)
    proxy.mark_bought(["cac2a709-896a-462b-9085-85ddb4f4a77c"])
    # items = proxy.get_items(["634b9d96-3787-459a-8def-addfc761c10c","7c0c9a60-8212-4e0a-af14-1f8758f3d199"])
    # print()
    # print(items)
    
    # print(rand_item())
    # print(rand_items())
    
    # items = rand_items()
    # bill = Bill(items)

    # print(bill)
    # print(bill.total_cost())
    # print(to_fancy_dollars(bill.total_cost()))

    # cart = Cart("alex", rand_items())
    # print(cart)
    # print(cart.total_cost())

    # print("bobbypin" in cart)
    # item = Item("bobbypin",3000,2000, localize(datetime.datetime.now()))
    # cart.add(item)
    # print("bobbypin" in cart)
    # cart.remove(item.item_id)
    # print("bobbypin" in cart)
    # receipt = cart.checkout("12813f09318jf1012813f09318jf1012813f09318jf1012813f09318jf10") # rand payment info
    # print(receipt)
    # print()
    # print(cart.to_data_dict())

    # print(receipt.to_console_str())



    # mongo_hostname = "cart-mongo-server"
    # mongo_port = "27017" # e.g. 27017
    # # base connection url = mongodb://{hostname}:{port}/


    # receipt_repo : ReceiptRepository = MongoDbReceiptRepository(hostname=mongo_hostname, port=mongo_port)
    # obj = receipt_repo.get("cc2c6e68-6c50-43e5-8cd6-84214ac6b511")
    # print(obj)
    # # # TODO: for now, UserService will use an admin token that lasts ~30 days from now (11/30/2022)
    # # # in future, this service needs to obtain an admin token it can use to ask User-service for admin-level
    # # # details on Users (payment info).
    # TEMP_ADMIN_SERVICE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NDcwMTVjOC1kODI4LTQwNGUtYjg3OC1lYThlNTRhMzk5ZDkiLCJpc3MiOiJ1c2VyLXNlcnZpY2UiLCJhdWQiOiJtcGNzNTEyMDUiLCJlbWFpbCI6Im1hdHRAbXBjcy5jb20iLCJuYW1lIjoibWF0dCIsImF1dGhvcml0aWVzIjpbIlJPTEVfVVNFUiIsIlJPTEVfQURNSU4iXSwiaWF0IjoxNjY5NDA4MDY2LCJleHAiOjE2NzIwMDAwNjZ9.N1x3fIBUz9CLDtabc9Lig6a4VFmRPdQaJwYX2Vabov0"
    # auction_connection_url = "http://auctions-service:10000"
    # proxy_auction_service : ProxyAuctionService = HTTPProxyAuctionService(auction_connection_url,TEMP_ADMIN_SERVICE_TOKEN)

    # item_id="71819d0b-12b9-4dc5-8402-e86642d37f17"
    # proxy_auction_service.stop_auction(item_id)

    # # user_service : ProxyUserService = HTTPProxyUserService(connection_url,TEMP_ADMIN_SERVICE_TOKEN)
    # user_service : ProxyUserService = StubbedProxyUserService()

    # user_id = "3f4fb3ca-05b3-4d5e-bd22-f9c99be5eb61"

    # info = user_service.fetch_payment_info(user_id)
    # print("paymentinfo: ",info)

 
    # data = {
    #     "id": 1001,
    #     "name": "geek",
    #     "passion": "coding",
    # }
    
    # response = requests.post(url, json=data)
    # response = requests.get(url)
    
    # print("Status Code", response.status_code)
    # print("JSON Response ", response.json())

    # JSON Response  {'timestamp': '2022-11-28T14:51:59.567+00:00', 'status': 400, 'error': 'Bad Request', 'path': '/item/012f81ca-307c-463c-d3da20c557d9'}

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
    # auctionRepo = MongoDbAuctionRepository("mongo-server")

    # bid1 = Bid.generate_basic_bid(100,200)
    # bid2 = Bid.generate_basic_bid(101,200)
    # bid3 = Bid.generate_basic_bid(102,200)
    # time_start1 = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=0, minute=0, second=0,microsecond=130002 ))
    # duration1 = datetime.timedelta(days=1)
    # auction1 = ClosedAuction.generate_auction([bid1,bid2,bid3],200,time_start1,duration1)

    # duration2 = datetime.timedelta(days=2)
    # auction2 = ClosedAuction.generate_auction([bid1,bid2,bid3],201,time_start1,duration2)

    # duration3 = datetime.timedelta(days=3)
    # auction3 = ClosedAuction.generate_auction([bid1,bid2,bid3],202,time_start1,duration3)
    # print("created 3 auctions; saving...")

    # auctionRepo.save_auction(auction1)
    # auctionRepo.save_auction(auction2)
    # auctionRepo.save_auction(auction3)

    # print()
    # print("now trying to retreive...")
    # auctionRepo.get_auction(auction1._item_id)
    # print()
    # print("changing data and saving changes...")
    # auction1._start_price_in_cents = 300000
    # auctionRepo.save_auction(auction1)
    # print()
    # print("now trying to retreive...")
    # auctionRepo.get_auction(auction1._item_id)
    # print()

    # print("fetching all")
    # left = time_start1 - datetime.timedelta(hours=2)
    # right = time_start1 + datetime.timedelta(days=4)
    # auctions = auctionRepo.get_auctions(left,right)

    # for auction in auctions:
    #     print(auction)
    # auctionRepo.check_server_status()
    # Issue the serverStatus command and print the results
    
if __name__ == "__main__":
    main()
    