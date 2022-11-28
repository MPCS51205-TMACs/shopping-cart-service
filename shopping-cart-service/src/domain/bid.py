# from __future__ import annotations
# import datetime
# from infrastructure import utils

# class Bid():

#     def __init__(
#         self,
#         bid_id : str,
#         item_id : str,
#         bidder_user_id : str,
#         amount_in_cents: int,
#         time_received: datetime.datetime,
#         active: bool) -> None:

#         self._bid_id = bid_id
#         self._item_id = item_id
#         self._bidder_user_id = bidder_user_id
#         self._amount_in_cents = amount_in_cents
#         self._time_received = time_received
#         self._active = active

#     def __repr__(self) -> str:
#         args = f"bid_id={self._bid_id}, "
#         args += f"item_id={self._item_id}, "
#         args += f"bidder_user_id={self._bidder_user_id}, "
#         args += "amount_in_cents=${:.2f}, ".format(self._amount_in_cents/100)
#         args += f"time_received={self._time_received}, "
#         args += f"active={self._active}"
#         return "Bid(" + args + ")" 

#     def convert_to_dict(self) -> dict:
#         """
#         returns a json-like representation of the internal contents
#         of a Bid.
#         """
        
#         return {
#             'bid_id': self._bid_id,
#             'item_id': self._item_id,
#             'bidder_user_id': self._bidder_user_id,
#             'amount_in_cents': self._amount_in_cents,
#             'time_received': utils.toSQLTimestamp6Repr(self._time_received),
#             'active': self._active,
#         }


#     def convert_to_dict_w_datetimes(self) -> dict:
#         """
#         returns a json-like representation of the internal contents
#         of a Bid. keeps time objects as datetime objects
#         """
        
#         return {
#             'bid_id': self._bid_id,
#             'item_id': self._item_id,
#             'bidder_user_id': self._bidder_user_id,
#             'amount_in_cents': self._amount_in_cents,
#             'time_received': self._time_received,
#             'str_time_received': utils.toSQLTimestamp6Repr(self._time_received),
#             'active': self._active,
#         }
        

#     @staticmethod    
#     def generate_basic_bid(bidId: int, itemId: int) -> Bid:
#         bid_id = str(bidId)
#         item_id = str(itemId)
#         bidder_user_id = "asclark"
#         amount_in_cents = 4000 # $40
#         time_received = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=0, minute=0, second=0,microsecond=130002 ))
#         active=True
#         return Bid(bid_id,item_id,bidder_user_id,amount_in_cents,time_received,active)