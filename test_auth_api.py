#!/usr/bin/env python3
"""
Test script for FreelanceX.AI Auth API
"""

import asyncio
import aiohttp
import json

async def test_auth_api():
    base_url = "http://127.0.0.1:8023"
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("Testing health endpoint...")
        async with session.get(f"{base_url}/health") as resp:
            print(f"Health: {await resp.json()}")
        
        # Test registration
        print("\nTesting registration...")
        register_data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
        async with session.post(f"{base_url}/register", json=register_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"Registration successful: {result}")
                user_id = result.get("id")
            else:
                print(f"Registration failed: {resp.status} - {await resp.text()}")
                return
        
        # Test login
        print("\nTesting login...")
        login_data = {
            "username": "test@example.com",
            "password": "password123"
        }
        async with session.post(f"{base_url}/login", data=login_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"Login successful: {result}")
                token = result.get("access_token")
            else:
                print(f"Login failed: {resp.status} - {await resp.text()}")
                return
        
        # Test chat save with auth
        print("\nTesting chat save...")
        headers = {"Authorization": f"Bearer {token}"}
        chat_data = {
            "role": "user",
            "content": "Hello, this is a test message!"
        }
        async with session.post(f"{base_url}/chat/save", json=chat_data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"Chat save successful: {result}")
            else:
                print(f"Chat save failed: {resp.status} - {await resp.text()}")
        
        # Test chat history
        print("\nTesting chat history...")
        async with session.get(f"{base_url}/chat/history", headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"Chat history: {len(result)} messages")
                for msg in result:
                    print(f"  - {msg['role']}: {msg['content'][:50]}...")
            else:
                print(f"Chat history failed: {resp.status} - {await resp.text()}")

if __name__ == "__main__":
    asyncio.run(test_auth_api())
