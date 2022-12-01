from typing import Dict, Any, Optional
import requests
from abc import ABC, abstractmethod
import string, random
from domain.utils import *

class ProxyUserService(ABC):

    @abstractmethod
    def fetch_payment_info(self, user_id: str) -> Optional[str]:
        pass

class StubbedProxyUserService(ProxyUserService):

    def __init__(self) -> None:
        pass

    def fetch_payment_info(self, user_id: str) -> Optional[str]:
        letters = string.digits
        payment_info = ( ''.join(random.choice(letters) for i in range(16)) )
        return payment_info

class HTTPProxyUserService(ProxyUserService):

    def __init__(self, connection_url: str, admin_auth_token: str) -> None:
        self._admin_auth_token = admin_auth_token # e.g. "eyJhbGciOiJIUzI1NiIs..."
        self._base_url = connection_url # e.g. http://user-service:8080

    def fetch_payment_info(self, user_id: str) -> Optional[str]:
        print(f"[HTTPProxyUserService] sending HTTP GET request to user-service (using an admin auth token) to get payment info on user_id={short_str(user_id)}")

        get_user_url = self._base_url + f"/user/admin/{user_id}/payment" # e.g. "http://item-service:8088" + "/user/admin/021309410341asdf/payment"
        headers={'Authorization': f'Bearer {self._admin_auth_token}'}
        response = requests.get(get_user_url, headers=headers)
        print(f"got status_code={response.status_code}")
        json_data : Dict[str,Any] = response.json()
        print(f"json response:\n {json_data}")
        payment_info = None
        if response.status_code == 200:
            for key, val in json_data.items():
                if "paymentinfo" == key.lower():
                    payment_info = str(val)
            if not payment_info : # payment_info is None or "": failed to find paymentinfo in response (or read an empty str for payment info)
                print("""see payment_info.py:fetch_payment_info(). 
                did not find payment info in response from user-service
                (or I did not interpret payment info from response correctly)! """)
                return None
            return payment_info
        else:
            print(f"""see payment_info.py:fetch_payment_info(). 
                did not get a 200 response from user-service; got {response.status_code}""")
            return None

