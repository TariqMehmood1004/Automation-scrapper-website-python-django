from dataclasses import dataclass
from typing import List


@dataclass
class CartItem:
    product_id: int
    quantity: int


@dataclass
class CheckoutData:
    items: List[CartItem]
    billing: dict
    shipping: dict