from __future__ import annotations
import json
from typing import List, Set
import sys
import datetime

from domain.closed_auction import ClosedAuction
from domain.bid import Bid
from infrastructure.utils import TIME_ZONE

from domain.auction_repository_mongo import MongoDbAuctionRepository

bids_filename = "db/exbids.txt"
auctions_filename = "db/exauctions.txt"

def generate_dummy_auctions() -> List[ClosedAuction]:
    
    bids = generate_dummy_bids()
    item_ids : Set[str] = set()
    for bid in bids:
        item_ids.add(bid._item_id)

    file = open(auctions_filename, 'r')
    lines = file.readlines()
    file.close()

    auctions : List[ClosedAuction] = []

    for line in lines:
        line=line.strip()
        entries = [entry.strip() for entry in line.split(",")]

        item_id = entries[0]
        seller_user_id = entries[1]
        start_price_in_cents = int(entries[2])
        format = "%Y-%m-%d %H:%M:%S.%f"
        start_time = TIME_ZONE.localize(datetime.datetime.strptime(entries[3],format))
        end_time = TIME_ZONE.localize(datetime.datetime.strptime(entries[4],format))
        cancel_time = TIME_ZONE.localize(datetime.datetime.strptime(entries[5],format)) if entries[5] != "" else None 
        finalized_time = TIME_ZONE.localize(datetime.datetime.strptime(entries[6],format))

        relevant_bids = []
        for bid in bids:
            if bid._item_id == item_id:
                relevant_bids.append(bid)

        new_auction = ClosedAuction(item_id,start_price_in_cents,start_time,end_time,cancel_time,finalized_time,relevant_bids)
        auctions.append(new_auction)


    return auctions
    
def generate_dummy_bids() -> List[Bid]:
    
    file = open(bids_filename, 'r')
    lines = file.readlines()
    file.close()

    bids : List[Bid] = []
    item_ids : Set[str] = set()

    for line in lines:
        line=line.strip()
        entries = [entry.strip() for entry in line.split(",")]

        bid_id = entries[0]
        item_id = entries[1]
        bidder_user_id = entries[2]
        amount_in_cents = int(entries[3])
        format = "%Y-%m-%d %H:%M:%S.%f"
        time_received = TIME_ZONE.localize(datetime.datetime.strptime(entries[4],format))
        active = entries[5]=="True"

        new_bid = Bid(bid_id,item_id,bidder_user_id,amount_in_cents,time_received,active)
        bids.append(new_bid)

    return bids
    

# def generate_dummy_auctions_csv() -> List[ClosedAuction]:
#     import csv

#     with open(filename, 'r') as file:
#         csvreader = csv.reader(file, delimiter=',')
#         for row in csvreader:
#             print(row)

if __name__ == "__main__":
    auctions = generate_dummy_auctions()
    bigauction = auctions[0]
    # bigauction.show_bid_history()
    
    # outputfile = "db/init/data.json"
    # with open(outputfile, 'w') as convert_file:
    #     convert_file.write(json.dumps([auction.convert_to_dict() for auction in auctions],indent=4))
    
    auction_repo = MongoDbAuctionRepository("mongo-server")

    for auction in auctions:
        print(f"saving: {auction}...",)
        auction_repo.save_auction(auction)