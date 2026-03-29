from bs4 import BeautifulSoup

def extract_nonce(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # print(f"[soup - extract_nonce] <=> {soup}")
    
    nonce_input = soup.find("button", {
        "name": "woocommerce_checkout_place_order"
    })
    
    print(f"[nonce_input - extract_nonce] <=> {nonce_input}")

    if not nonce_input:
        raise Exception("Extract Nonce not found")

    return nonce_input.get("value")