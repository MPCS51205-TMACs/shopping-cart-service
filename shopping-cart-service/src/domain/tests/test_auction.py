from typing import List
import pytest
import json
import datetime
from infrastructure.utils import TIME_ZONE

from domain.bid import Bid
from domain.closed_auction import ClosedAuction

class TestBid:

    def setup_class(cls):
        """this code runs before this whole test module runs"""
        bid1 = Bid.generate_basic_bid(100,200)
        bid2 = Bid.generate_basic_bid(101,200)
        bid3 = Bid.generate_basic_bid(102,200)
        auction = ClosedAuction.generate_auction([bid1,bid2,bid3],200)
        cls.auction = auction

    def test_display(cls):
        print(cls.auction)

