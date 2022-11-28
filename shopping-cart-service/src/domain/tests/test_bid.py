import pytest
import json
import datetime
from infrastructure.utils import TIME_ZONE

from domain.bid import Bid

class TestBid:

    def setup_class(cls):
        """this code runs before this whole test module runs"""
        cls.bid1 = generate_basic_bid()

    def test_display(cls):
        print(cls.bid1)

def generate_basic_bid() -> Bid:
    bid_id = "100"
    item_id = "200"
    bidder_user_id = "asclark"
    amount_in_cents = 4000 # $40
    time_received = TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=0, minute=0, second=0,microsecond=130002 ))
    active=True
    return Bid(bid_id,item_id,bidder_user_id,amount_in_cents,time_received,active)