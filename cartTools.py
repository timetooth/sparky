from utils import get_node_base_uri, User
from agents import function_tool, RunContextWrapper
import requests
import json

node_base_url = get_node_base_uri()

@function_tool
def add_item_to_cart(context: RunContextWrapper[User],quantity: int, product_id: int,color: str=None,size: str=None) -> str :
    """
    Add an item to the user's cart in the Walmart application.
    Args:
        quantity (int): The quantity of the product to add to the cart (Necessary).
        product_id (int): The Product ID of the product to add to the cart (Necessary).
        color (str, optional): The color of the product. Defaults to None (Optional).
        size (str, optional): The size of the product. Defaults to None (Optional).
    """
    print("-----------------Adding Item To Cart Tool-----------------")

    jwt_token = context.context.user_jwt
    if not jwt_token:
        return "No user JWT token was provided."
    url = node_base_url + f"/app/cart/add"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    
    payload = {
        "quantity":quantity,
        "productId":product_id,
    }
    if color: payload["color"]=color
    if size: payload["size"]=size

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        response_data = response.json()
        success = response_data.get('success', False)
        reason = response_data.get('reason', 'No reason provided')
        if success:
            return f"Item with Product ID {product_id} added to cart successfully."
        else:
            return "Item could not be added, Reason: " + reason

    elif response.status_code == 404:
        return "Failed to add item to cart."
    
    return "Trouble adding products to cart"

@function_tool
def get_all_items_in_cart(context: RunContextWrapper[User]) -> str:
    """
    Get all items in the user's cart in the Walmart application.
    
    Returns:
        str: Details of all items in the cart, or an error message if the cart is empty or an error occurs.
    """
    print("-----------------Getting All Items In Cart Tool-----------------")
    
    jwt_token = context.context.user_jwt
    if not jwt_token:
        return "No user JWT token was provided."
    url = node_base_url + f"/app/cart"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    
    response = requests.get(url, headers=headers)

    cart_items = []
    if response.status_code == 200:
        response_data = response.json()
        success = response_data.get('success', False)
        if success:
            products = response_data.get('data', {}).get('products', [])
            for product in products:
                if product: cart_items.append(product.get('embedding_text', 'No details available for this product.'))
            ret = "All items in the cart:\n"
            ret += '\n'.join(cart_items) if cart_items else "No items in the cart."
            return ret
        else:
            return "Failed to fetch cart items, Reason: " + response_data.get('reason', 'No reason provided')
    
    elif response.status_code == 404:
        return "Cart not found."
    
    return "Trouble fetching cart items"

@function_tool
def remove_all_items(context: RunContextWrapper[User]) -> str:
    """
    Removes all items from the user's cart in the Walmart application.
    
    Returns:
        str: Confirmation message if successful, or an error message if the cart is empty or an error occurs.
    """
    print("-----------------Removing All Items In Cart Tool-----------------")
    
    jwt_token = context.context.user_jwt
    if not jwt_token:
        return "No user JWT token was provided."
    url = node_base_url + f"/app/cart/clearCart"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    
    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        success = response_data.get('success', False)
        if success:
            return "All items removed from the cart successfully."
        else:
            return "Failed to remove items from cart, Reason: " + response_data.get('reason', 'No reason provided')
    
    elif response.status_code == 404:
        return "Cart not found."
    
    return "Trouble removing items from cart"

@function_tool
def remove_item_from_cart(context: RunContextWrapper[User], product_id: int, color: str = None, size: str = None) -> str:
    """
    Remove an item from the user's cart in the Walmart application.
    
    Args:
        product_id (int): The Product ID of the product to remove from the cart (Necessary).
    
    Returns:
        str: Confirmation message if successful, or an error message if the item is not found or an error occurs.
    """
    print("-----------------Removing Item From Cart Tool-----------------")
    
    jwt_token = context.context.user_jwt
    if not jwt_token:
        return "No user JWT token was provided."
    url = node_base_url + f"/app/cart/remove/{product_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    
    payload = {"productId":product_id}
    if color: payload["color"]=color
    if size: payload["size"]=size

    response = requests.delete(url, headers=headers, json=payload)

    if response.status_code == 200:
        response_data = response.json()
        success = response_data.get('success', False)
        if success:
            return f"Item with Product ID {product_id} removed from cart successfully."
        else:
            return "Failed to remove item from cart, Reason: " + response_data.get('reason', 'No reason provided')
    
    elif response.status_code == 404:
        return "Item not found in cart."
    
    return "Trouble removing item from cart"