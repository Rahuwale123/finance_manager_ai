#!/usr/bin/env python3
"""
Test script for FarmerX API
Run this to test the basic functionality
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

def test_transaction_message(message, expected_tool=None):
    """Test the main transaction message endpoint"""
    print(f"\n🔍 Testing message: '{message}'")
    
    payload = {
        "user_id": "test_user_123",
        "client_id": "farmer_x",
        "message": message
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/llm/transaction-message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Message processed successfully")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if expected_tool and result.get("tool_called") != expected_tool:
                print(f"⚠️  Expected tool '{expected_tool}' but got '{result.get('tool_called')}'")
            else:
                print(f"✅ Tool called: {result.get('tool_called')}")
                
        else:
            print(f"❌ Message processing failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Message processing error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting FarmerX API Tests")
    print("=" * 50)
    
    # Test basic endpoints
    test_health_check()
    test_root_endpoint()
    
    # Test transaction messages
    test_cases = [
        {
            "message": "I sold 10kg tomatoes for 1200 today",
            "expected_tool": "add_transaction"
        },
        {
            "message": "Paid 800 for fertilizers yesterday",
            "expected_tool": "add_transaction"
        },
        {
            "message": "Show me all expenses from this month",
            "expected_tool": "get_transaction"
        },
        {
            "message": "What are my incomes today?",
            "expected_tool": "get_transaction"
        }
    ]
    
    for test_case in test_cases:
        test_transaction_message(
            test_case["message"], 
            test_case["expected_tool"]
        )
        time.sleep(1)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")

if __name__ == "__main__":
    main() 