#!/bin/bash

# Test script for authentication system
# Make sure the server is running before executing this script

BASE_URL="http://localhost:8080/api/v4/auth"

echo "=== Testing Authentication System ==="

# Test 1: Register a new user
echo "1. Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpassword123"}')

echo "Register Response: $REGISTER_RESPONSE"

# Extract tokens from register response
ACCESS_TOKEN=$(echo $REGISTER_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
REFRESH_TOKEN=$(echo $REGISTER_RESPONSE | grep -o '"refresh_token":"[^"]*"' | cut -d'"' -f4)

echo "Access Token: $ACCESS_TOKEN"
echo "Refresh Token: $REFRESH_TOKEN"

# Test 2: Login with the same user
echo -e "\n2. Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpassword123"}')

echo "Login Response: $LOGIN_RESPONSE"

# Extract tokens from login response
LOGIN_ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
LOGIN_REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"refresh_token":"[^"]*"' | cut -d'"' -f4)

# Test 3: Refresh token
echo -e "\n3. Testing token refresh..."
REFRESH_RESPONSE=$(curl -s -X POST "${BASE_URL}/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$LOGIN_REFRESH_TOKEN\"}")

echo "Refresh Response: $REFRESH_RESPONSE"

# Extract new tokens
NEW_ACCESS_TOKEN=$(echo $REFRESH_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
NEW_REFRESH_TOKEN=$(echo $REFRESH_RESPONSE | grep -o '"refresh_token":"[^"]*"' | cut -d'"' -f4)

# Test 4: Logout (revoke refresh token)
echo -e "\n4. Testing logout..."
LOGOUT_RESPONSE=$(curl -s -X POST "${BASE_URL}/logout" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$NEW_REFRESH_TOKEN\"}")

echo "Logout Response: $LOGOUT_RESPONSE"

# Test 5: Try to use revoked refresh token (should fail)
echo -e "\n5. Testing revoked refresh token (should fail)..."
FAILED_REFRESH_RESPONSE=$(curl -s -X POST "${BASE_URL}/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$NEW_REFRESH_TOKEN\"}")

echo "Failed Refresh Response: $FAILED_REFRESH_RESPONSE"

# Test 6: Test logout-all with access token
echo -e "\n6. Testing logout-all..."
LOGOUT_ALL_RESPONSE=$(curl -s -X POST "${BASE_URL}/logout-all" \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN")

echo "Logout All Response: $LOGOUT_ALL_RESPONSE"

echo -e "\n=== Authentication Tests Complete ==="
