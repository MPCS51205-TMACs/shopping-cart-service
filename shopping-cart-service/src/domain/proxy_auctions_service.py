from typing import Dict, Any, Optional
import requests
from abc import ABC, abstractmethod
import string, random
from domain.utils import *

class ProxyAuctionService(ABC):

    @abstractmethod
    def stop_auction(self, item_id: str) -> bool:
        pass

class StubbedProxyAuctionService(ProxyAuctionService):

    def __init__(self) -> None:
        pass

    def stop_auction(self, item_id: str) -> bool:
        return True

class HTTPProxyAuctionService(ProxyAuctionService):

    def __init__(self, connection_url: str, admin_auth_token: str) -> None:
        self._admin_auth_token = admin_auth_token # e.g. "eyJhbGciOiJIUzI1NiIs..."
        self._base_url = connection_url # e.g. http://user-service:8080

    def stop_auction(self, item_id: str) -> bool:
        print(f"[HTTPProxyAuctionService] sending HTTP POST request to auction-service (using an admin auth token) to stop auction on item_id={short_str(item_id)}")
        post_auction_url = self._base_url + f"/api/v1/stopAuction/{item_id}" # e.g. "http://item-service:8088" + "/api/v1/stopAuction/dakslf134lk342j65lkj"
        headers={'Authorization': f'Bearer {self._admin_auth_token}'}
        response = requests.post(post_auction_url, headers=headers)
        print(f"got status_code={response.status_code}")
        json_data : Dict[str,Any] = response.json()
        print(f"json response:\n {json_data}")
        if response.status_code == 200:
            return True
        if response.status_code == 401:
            print(f"[HTTPProxyAuctionService] my admin token was not validated! UPDATE ME")
            return False
        return False

