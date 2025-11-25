#!/usr/bin/env python3
"""
Test script for aiFeedback API endpoint
Run this from the project root directory
"""
import requests
import json

# Test data
test_data = {
    "text": "Agent: Hi there! Today, which topic do you want to talk about? User: I want to talk about Vietnam's history.Agent: That sounds great! Vietnam has a long and fascinating history. Which period are you most interested in — ancient dynasties, the colonial era, or modern history?User: I think I'd like to start with the time when Vietnam was under French rule. Agent: Excellent choice. Do you know when the French colonized Vietnam?User: Hmm, I think it was in the 19th century, right? Agent: Exactly! The French began their colonization in the mid-1800s. How do you feel about discussing how this period influenced Vietnamese culture and education? User: That would be great! I want to improve my vocabulary while learning about it."
}

url = "http://127.0.0.1:8080/aiFeedback"

print("Testing aiFeedback API endpoint...")
print(f"URL: {url}")
print(f"Method: POST")
print(f"Data: {json.dumps(test_data, indent=2)}")
print("-" * 50)

try:
    response = requests.post(
        url,
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print("-" * 50)
    
    if response.status_code == 200:
        print("✅ Success!")
        result = response.json()
        print(f"Feedback: {result.get('feedback', 'N/A')[:200]}...")  # Show first 200 chars
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Connection Error: Make sure the server is running on port 8080")
    print("   Start the server with: cd backend && python server.py")
except requests.exceptions.Timeout:
    print("❌ Timeout: The request took too long")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {str(e)}")

