#!/usr/bin/env python3
"""API Testing Script for Flipkart Monolith Application."""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:5000"
admin_token = None
user_token = None


def print_response(title: str, response: requests.Response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_health_check():
    """Test health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    return response.status_code == 200


def test_register_user():
    """Test user registration."""
    data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "test123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "1234567890"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print_response("User Registration", response)
    
    if response.status_code == 201:
        global user_token
        user_token = response.json().get('access_token')
    return response.status_code in [201, 409]  # 409 if already exists


def test_login_admin():
    """Test admin login."""
    data = {
        "email": "admin@flipkart.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    print_response("Admin Login", response)
    
    if response.status_code == 200:
        global admin_token
        admin_token = response.json().get('access_token')
    return response.status_code == 200


def test_login_user():
    """Test user login."""
    data = {
        "email": "john@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    print_response("User Login", response)
    
    if response.status_code == 200:
        global user_token
        user_token = response.json().get('access_token')
    return response.status_code == 200


def test_get_categories():
    """Test getting categories."""
    response = requests.get(f"{BASE_URL}/api/categories")
    print_response("Get Categories", response)
    return response.status_code == 200


def test_get_products():
    """Test getting products with filters."""
    params = {
        "page": 1,
        "per_page": 5,
        "search": "phone",
        "sort_by": "price",
        "sort_order": "asc"
    }
    response = requests.get(f"{BASE_URL}/api/products", params=params)
    print_response("Get Products (Filtered)", response)
    return response.status_code == 200


def test_get_product_details():
    """Test getting product details."""
    response = requests.get(f"{BASE_URL}/api/products/1")
    print_response("Get Product Details", response)
    return response.status_code == 200


def test_add_to_cart():
    """Test adding product to cart."""
    if not user_token:
        print("❌ Skipping - User not logged in")
        return False
    
    headers = {"Authorization": f"Bearer {user_token}"}
    data = {"product_id": 1, "quantity": 2}
    response = requests.post(f"{BASE_URL}/api/cart/add", json=data, headers=headers)
    print_response("Add to Cart", response)
    return response.status_code in [201, 200]


def test_get_cart():
    """Test getting cart."""
    if not user_token:
        print("❌ Skipping - User not logged in")
        return False
    
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BASE_URL}/api/cart", headers=headers)
    print_response("Get Cart", response)
    return response.status_code == 200


def test_get_profile():
    """Test getting user profile."""
    if not user_token:
        print("❌ Skipping - User not logged in")
        return False
    
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BASE_URL}/api/users/profile", headers=headers)
    print_response("Get User Profile", response)
    return response.status_code == 200


def test_create_product():
    """Test creating product (admin only)."""
    if not admin_token:
        print("❌ Skipping - Admin not logged in")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 999,
        "discount_percentage": 10,
        "category_id": 1,
        "brand": "TestBrand",
        "stock_quantity": 50,
        "sku": f"TEST{hash('test') % 10000}",
        "image_url": "https://via.placeholder.com/300"
    }
    response = requests.post(f"{BASE_URL}/api/products", json=data, headers=headers)
    print_response("Create Product (Admin)", response)
    return response.status_code in [201, 409]


def run_all_tests():
    """Run all API tests."""
    print("\n" + "="*60)
    print("  Flipkart Monolith API Testing Suite")
    print("="*60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Get Categories", test_get_categories),
        ("Get Products", test_get_products),
        ("Get Product Details", test_get_product_details),
        ("Admin Login", test_login_admin),
        ("User Login", test_login_user),
        ("Register User", test_register_user),
        ("Get User Profile", test_get_profile),
        ("Add to Cart", test_add_to_cart),
        ("Get Cart", test_get_cart),
        ("Create Product (Admin)", test_create_product),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    print("="*60)


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
