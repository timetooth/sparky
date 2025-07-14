import requests
import json
from agents import function_tool
from utils import get_node_base_uri

node_base_url = get_node_base_uri()

@function_tool
def search_by_category(category: str, limit: int = 15) -> str :
    """
    Search for products by category from the Database. 
    Category should be one of:
        ['Beauty' 'Home' 'Clothing' 'Sports & Outdoors' 'Food' 'Jewelry'
        'Personal Care' 'Patio & Garden' 'Health and Medicine' 'Pets'
        'Premium Beauty' 'Baby' 'Household Essentials' 'Home Improvement'
        'Shop with Purpose' 'Party & Occasions' 'Electronics' 'Collectibles'
        'Arts Crafts & Sewing' 'Subscriptions' 'Toys' 'Seasonal' 'Auto & Tires']
    Args:
        category (str): The category to search in.
        limit (int): The number of products to return. Default is 20.
    """
    print("-----------------Searched by cat-----------------")
    url = node_base_url + f"/app/search/category/{category}?page=1&limit={limit}"
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = json.loads(response.text)
        product_data = response_data.get('products',[])
        products = [product.get('embedding_text','') for product in product_data]
        return '\n'.join(products)

    elif response.status_code == 404:
        return "No products found in this category."
    
    return "Trouble fetching products"

@function_tool
def search_by_id(product_id: int) -> str:
    """
    Search for a product by its Product ID from the Database.
    
    Args:
        product_id (int): The Product ID of the product to search for.
    
    Returns:
        str: Details of the product if found, otherwise an error message.
    """
    print("-----------------Searched by Id-----------------")
    url = node_base_url + f"/app/search/id/{product_id}"
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        response_data = json.loads(response.text)
        return response_data.get('product', {}).get('embedding_text', 'No details available for this product.')
    
    elif response.status_code == 404:
        return "Product not found."
    
    return "Trouble fetching product details"

@function_tool
def fuzzy_search(query: str, limit: int = 15) -> str:
    """
    Perform a fuzzy search for products based on a query string from the Database.
    
    Args:
        query (str): The search query string.
        limit (int): The number of products to return. Default is 15.
    
    Returns:
        str: Details of the products found, or an error message if no products are found.
    """
    print("-----------------Searched by Fuzzy-----------------")
    url = node_base_url + f"/app/search/fuzzy?q={query}&page=1&limit={limit}$page=1"
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        response_data = json.loads(response.text)
        product_data = response_data.get('products', [])
        products = [product.get('embedding_text', '') for product in product_data]
        return '\n'.join(products)
    
    elif response.status_code == 404:
        return "No products found matching the query."
    
    return "Trouble fetching products"