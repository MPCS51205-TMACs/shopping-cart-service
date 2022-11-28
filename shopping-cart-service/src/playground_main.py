# from typing import Optional, Union, Dict

# from application.closed_auction_metrics_service import ClosedAuctionMetricsService
# from domain.auction_repository import AuctionRepository, InMemoryAuctionRepository
# from domain.auction_repository_mongo import MongoDbAuctionRepository
# from infrastructure import utils
# from domain.bid import Bid
# from domain.closed_auction import ClosedAuction

# import datetime
import requests
from domain.item_repository import HTTPProxyItemRepository

def main():
    # item_id = "012f81ca-307c-463c-d3da20c557d9"
    url = "http://item-service:8088/"

    proxy = HTTPProxyItemRepository(url)
    items = proxy.get_items(["634b9d96-3787-459a-8def-addfc761c10c","7c0c9a60-8212-4e0a-af14-1f8758f3d199"])
    print()
    print(items)
 
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
    