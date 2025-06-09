import json
import requests
from typing import Optional, Tuple
from django.conf import settings

class ZarinpalGateway:
    SANDBOX_URL = "https://sandbox.zarinpal.com/pg/rest/WebGate/"
    MAIN_URL = "https://www.zarinpal.com/pg/rest/WebGate/"
    
    def __init__(self, merchant_id: str, callback_url: str, sandbox: bool = False):
        self.merchant_id = merchant_id
        self.callback_url = callback_url
        self.base_url = self.SANDBOX_URL if sandbox else self.MAIN_URL

    def request_payment(
        self,
        amount: int,
        description: str,
        email: Optional[str] = None,
        mobile: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Request a payment URL from Zarinpal
        Returns: (success, authority or error_message)
        """
        data = {
            "MerchantID": self.merchant_id,
            "Amount": amount,
            "Description": description,
            "CallbackURL": self.callback_url,
            "Email": email,
            "Mobile": mobile
        }
        
        try:
            response = requests.post(
                f"{self.base_url}PaymentRequest.json",
                json=data,
                timeout=10
            )
            result = response.json()
            
            if result["Status"] == 100:
                return True, result["Authority"]
            return False, f"Error {result['Status']}: {result['Message']}"
            
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except json.JSONDecodeError:
            return False, "Invalid response from gateway"

    def verify_payment(
        self,
        authority: str,
        amount: int
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Verify a payment
        Returns: (success, ref_id or error_message, status_code)
        """
        data = {
            "MerchantID": self.merchant_id,
            "Authority": authority,
            "Amount": amount
        }
        
        try:
            response = requests.post(
                f"{self.base_url}PaymentVerification.json",
                json=data,
                timeout=10
            )
            result = response.json()
            
            if result["Status"] == 100:
                return True, result["RefID"], str(result["Status"])
            return False, f"Error: {result['Message']}", str(result["Status"])
            
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}", None
        except json.JSONDecodeError:
            return False, "Invalid response from gateway", None
