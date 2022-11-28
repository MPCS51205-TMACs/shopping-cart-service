from pydantic import BaseModel
from typing import List

# expected data types and fields of body content
# from incoming requests to add auction data

# class AuctionData(BaseModel):
#     item_id : str

# class BidData(BaseModel):
#     bid_id : str

# class AddAuctionDataRequest(BaseModel):
#     auction: AuctionData
#     bids: List[BidData]
#     winning_bid: BidData

# class AddAuctionDataResponse(BaseModel):
#     success: bool
#     message: str

# expected data types and fields of body content
# from incoming requests to get closed auction data

class GetAuctionDataRequest(BaseModel):
    item_id: str

class GetAuctionDataResponse(BaseModel):
    item_id: str