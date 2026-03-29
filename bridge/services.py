import requests
from django.conf import settings
from .parsers import extract_nonce


class WooBridgeService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(settings.DEFAULT_HEADERS)

    def add_to_cart(self, item):
        """
        item: dict with keys product_id, quantity, variation_id, attributes
        """
        url = f"{settings.BASE_URL}/?wc-ajax=add_to_cart"
        print(f"[URL - WooBridgeService - add_to_cart] <=> {url}")
        
        data = {
            "add-to-cart": item["product_id"],
            "product_id": item["product_id"],
            "variation_id": item.get("variation_id", ""),
            "quantity": item["quantity"]
        }

        # Add attributes for variable product
        if "attributes" in item and item["attributes"]:
            for attr_key, attr_value in item["attributes"].items():
                # WooCommerce expects "attribute_pa_{slug}" keys
                data[f"attribute_{attr_key}"] = attr_value

        res = self.session.post(url, data=data)
        print(f"[RES - WooBridgeService - add_to_cart] <=> {res.text}")
        try:
            response = res.json()
        except Exception:
            raise Exception(f"Add to cart failed, non-JSON response: {res.text}")

        if res.status_code != 200 or response.get("error"):
            raise Exception(f"Add to cart failed: {response}")

        return response

    def get_checkout_nonce(self):
        url = f"{settings.BASE_URL}/checkout/"
        res = self.session.get(url)
        if res.status_code != 200:
            raise Exception("Failed to fetch checkout page")
        return extract_nonce(res.text)

    def checkout(self, billing, shipping, nonce):
        url = f"{settings.BASE_URL}/?wc-ajax=checkout"

        # If shipping not provided → use billing
        if not shipping:
            shipping = {
                "shipping_first_name": billing.get("billing_first_name"),
                "shipping_last_name": billing.get("billing_last_name"),
                "shipping_country": billing.get("billing_country"),
                "shipping_address_1": billing.get("billing_address_1"),
                "shipping_address_2": billing.get("billing_address_2"),
                "shipping_city": billing.get("billing_city"),
                "shipping_state": billing.get("billing_state"),
                "shipping_postcode": billing.get("billing_postcode"),
            }

        payload = {
            **billing,
            **shipping,

            # Core checkout fields
            "payment_method": "noonpay",
            "shipping_method[0]": "flat_rate:1",
            "woocommerce_checkout_place_order": "Place order",

            # Required Woo fields
            "woocommerce-process-checkout-nonce": nonce,
            "_wp_http_referer": "/?wc-ajax=update_order_review",

            # Optional but improves success
            "wc_order_attribution_source_type": "typein",
            "wc_order_attribution_utm_source": "(direct)",
            "wc_order_attribution_session_entry": f"{settings.BASE_URL}/product/",
            "wc_order_attribution_user_agent": self.session.headers.get("User-Agent"),
        }

        res = self.session.post(url, data=payload)
        print(f"[RES - WooBridgeService - checkout] <=> {res.text}")
        
        try:
            data = res.json()
        except Exception:
            raise Exception(f"Checkout failed: {res.text}")

        if data.get("result") != "success":
            raise Exception(f"Checkout error: {data}")

        return data.get("redirect")

    def process_order(self, items, billing, shipping):
        print(f"[INFO - WooBridgeService - process_order] <=> {items}")
        
        # 1. Add each item to cart
        for item in items:
            self.add_to_cart(item)

        # 2. Get nonce for checkout
        nonce = self.get_checkout_nonce()
        print(f"[nonce - WooBridgeService - process_order] <=> {nonce}")

        # 3. Checkout
        redirect_url = self.checkout(billing, shipping, nonce)
        return redirect_url