#!/bin/bash
# =============================================================
# IPI Investor Flow - Complete API Test Script
# =============================================================
# Run from terminal or use the curl commands individually in Postman
#
# Usage: bash test_investor_flow.sh
# =============================================================

BASE_URL="http://20.20.21.41:5001/api/v1"

# Test user credentials
TEST_EMAIL="testinvestor$(date +%s)@test.com"
TEST_PASSWORD="Test@12345"
TEST_NAME="Test Investor"
TEST_PHONE="01012345678"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_step() {
    echo ""
    echo "============================================================="
    echo -e "${CYAN}STEP $1: $2${NC}"
    echo "============================================================="
}

print_result() {
    echo -e "${YELLOW}Response:${NC}"
    echo "$1" | python3 -m json.tool 2>/dev/null || echo "$1"
    echo ""
}

# =============================================================
# STEP 1: REGISTER - Send OTP
# =============================================================
print_step "1" "REGISTER - Send OTP to email"

RESPONSE=$(curl -s -X POST "$BASE_URL/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$TEST_NAME\",
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"phone\": \"$TEST_PHONE\"
  }")

print_result "$RESPONSE"

echo -e "${YELLOW}Enter the OTP code you received by email (or press Enter to skip to direct register):${NC}"
read -r OTP_CODE

if [ -n "$OTP_CODE" ]; then
    # =============================================================
    # STEP 2: VERIFY OTP
    # =============================================================
    print_step "2" "VERIFY OTP and complete registration"

    RESPONSE=$(curl -s -X POST "$BASE_URL/auth/verify-otp" \
      -H "Content-Type: application/json" \
      -d "{
        \"email\": \"$TEST_EMAIL\",
        \"otp\": \"$OTP_CODE\"
      }")

    print_result "$RESPONSE"

    ACCESS_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('access_token',d.get('access_token','')))" 2>/dev/null)
    REFRESH_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('refresh_token',d.get('refresh_token','')))" 2>/dev/null)
else
    # =============================================================
    # STEP 2 (ALT): DIRECT REGISTER (no email verification)
    # =============================================================
    print_step "2" "DIRECT REGISTER (legacy, no OTP)"

    RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
      -H "Content-Type: application/json" \
      -d "{
        \"name\": \"$TEST_NAME\",
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\",
        \"phone\": \"$TEST_PHONE\"
      }")

    print_result "$RESPONSE"

    ACCESS_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('access_token',d.get('access_token','')))" 2>/dev/null)
    REFRESH_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('refresh_token',d.get('refresh_token','')))" 2>/dev/null)
fi

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "" ]; then
    echo -e "${RED}Registration failed. Trying login instead...${NC}"

    # =============================================================
    # STEP 2 (FALLBACK): LOGIN
    # =============================================================
    print_step "2" "LOGIN (user may already exist)"

    RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
      -H "Content-Type: application/json" \
      -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\"
      }")

    print_result "$RESPONSE"

    ACCESS_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('access_token',d.get('access_token','')))" 2>/dev/null)
    REFRESH_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('refresh_token',d.get('refresh_token','')))" 2>/dev/null)
fi

echo -e "${GREEN}Access Token: ${ACCESS_TOKEN:0:50}...${NC}"
echo -e "${GREEN}Refresh Token: ${REFRESH_TOKEN:0:50}...${NC}"

# =============================================================
# STEP 3: GET MY PROFILE
# =============================================================
print_step "3" "GET MY PROFILE (/auth/me)"

RESPONSE=$(curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_result "$RESPONSE"

# =============================================================
# STEP 4: UPDATE FCM TOKEN (for push notifications)
# =============================================================
print_step "4" "UPDATE FCM TOKEN (enable push notifications)"

RESPONSE=$(curl -s -X POST "$BASE_URL/user/update-fcm-token" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "fcm_token": "test_fcm_token_from_script_12345"
  }')

print_result "$RESPONSE"

# =============================================================
# STEP 5: GET DASHBOARD DATA
# =============================================================
print_step "5" "GET DASHBOARD DATA"

RESPONSE=$(curl -s -X GET "$BASE_URL/user/dashboard" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_result "$RESPONSE"

# =============================================================
# STEP 6: BROWSE APARTMENTS
# =============================================================
print_step "6" "BROWSE APARTMENTS (marketplace)"

RESPONSE=$(curl -s -X GET "$BASE_URL/apartments?page=1&per_page=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_result "$RESPONSE"

# Save first apartment ID
APARTMENT_ID=$(echo "$RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
items = d.get('data',{}).get('apartments', d.get('data',{}).get('items', d.get('apartments',[])))
if isinstance(items, list) and len(items) > 0:
    print(items[0].get('id',''))
else:
    print('')
" 2>/dev/null)

echo -e "${GREEN}First Apartment ID: $APARTMENT_ID${NC}"

# =============================================================
# STEP 7: GET APARTMENT DETAILS
# =============================================================
if [ -n "$APARTMENT_ID" ] && [ "$APARTMENT_ID" != "" ]; then
    print_step "7" "GET APARTMENT DETAILS (ID: $APARTMENT_ID)"

    RESPONSE=$(curl -s -X GET "$BASE_URL/apartments/$APARTMENT_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    print_result "$RESPONSE"
else
    print_step "7" "SKIP - No apartments found"
fi

# =============================================================
# STEP 8: BROWSE CARS
# =============================================================
print_step "8" "BROWSE CARS (marketplace)"

RESPONSE=$(curl -s -X GET "$BASE_URL/cars?page=1&per_page=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_result "$RESPONSE"

# Save first car ID
CAR_ID=$(echo "$RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
items = d.get('data',{}).get('cars', d.get('data',{}).get('items', d.get('cars',[])))
if isinstance(items, list) and len(items) > 0:
    print(items[0].get('id',''))
else:
    print('')
" 2>/dev/null)

echo -e "${GREEN}First Car ID: $CAR_ID${NC}"

# =============================================================
# STEP 9: GET CAR DETAILS
# =============================================================
if [ -n "$CAR_ID" ] && [ "$CAR_ID" != "" ]; then
    print_step "9" "GET CAR DETAILS (ID: $CAR_ID)"

    RESPONSE=$(curl -s -X GET "$BASE_URL/cars/$CAR_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    print_result "$RESPONSE"
else
    print_step "9" "SKIP - No cars found"
fi

# =============================================================
# STEP 10: SUBMIT APARTMENT INVESTMENT REQUEST (with KYC)
# =============================================================
if [ -n "$APARTMENT_ID" ] && [ "$APARTMENT_ID" != "" ]; then
    print_step "10" "SUBMIT APARTMENT INVESTMENT REQUEST (with KYC docs)"

    # Create dummy test files for KYC documents
    echo "test" > /tmp/test_id_front.jpg
    echo "test" > /tmp/test_id_back.jpg
    echo "test" > /tmp/test_proof.jpg

    RESPONSE=$(curl -s -X POST "$BASE_URL/investments/request" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -F "apartment_id=$APARTMENT_ID" \
      -F "shares_requested=1" \
      -F "full_name=$TEST_NAME" \
      -F "phone=$TEST_PHONE" \
      -F "national_id=29001011234567" \
      -F "address=123 Test Street, Cairo" \
      -F "date_of_birth=1990-01-01" \
      -F "nationality=Egyptian" \
      -F "occupation=Engineer" \
      -F "id_document_front=@/tmp/test_id_front.jpg" \
      -F "id_document_back=@/tmp/test_id_back.jpg" \
      -F "proof_of_address=@/tmp/test_proof.jpg")

    print_result "$RESPONSE"

    REQUEST_ID=$(echo "$RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('data',{}).get('request_id', d.get('data',{}).get('id','')))
" 2>/dev/null)

    echo -e "${GREEN}Investment Request ID: $REQUEST_ID${NC}"
else
    print_step "10" "SKIP - No apartments to invest in"
fi

# =============================================================
# STEP 11: SUBMIT CAR INVESTMENT REQUEST (with KYC)
# =============================================================
if [ -n "$CAR_ID" ] && [ "$CAR_ID" != "" ]; then
    print_step "11" "SUBMIT CAR INVESTMENT REQUEST (with KYC docs)"

    RESPONSE=$(curl -s -X POST "$BASE_URL/cars/investment-request" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -F "car_id=$CAR_ID" \
      -F "shares_requested=1" \
      -F "full_name=$TEST_NAME" \
      -F "phone=$TEST_PHONE" \
      -F "national_id=29001011234567" \
      -F "address=123 Test Street, Cairo" \
      -F "date_of_birth=1990-01-01" \
      -F "nationality=Egyptian" \
      -F "occupation=Engineer" \
      -F "id_document_front=@/tmp/test_id_front.jpg" \
      -F "id_document_back=@/tmp/test_id_back.jpg" \
      -F "proof_of_address=@/tmp/test_proof.jpg")

    print_result "$RESPONSE"
else
    print_step "11" "SKIP - No cars to invest in"
fi

# =============================================================
# STEP 12: GET MY INVESTMENT REQUESTS (Apartments)
# =============================================================
print_step "12" "GET MY APARTMENT INVESTMENT REQUESTS"

RESPONSE=$(curl -s -X GET "$BASE_URL/investments/requests" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_result "$RESPONSE"

# =============================================================
# STEP 13: GET MY CAR INVESTMENT REQUESTS
# =============================================================
print_step "13" "GET MY CAR INVESTMENT REQUESTS"

RESPONSE=$(curl -s -X GET "$BASE_URL/cars/investment-requests" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_result "$RESPONSE"

# =============================================================
# STEP 14: GET MY INVESTMENTS (shares I own)
# =============================================================
print_step "14" "GET MY APARTMENT INVESTMENTS (shares owned)"

RESPONSE=$(curl -s -X GET "$BASE_URL/shares/my-investments" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_result "$RESPONSE"

# =============================================================
# STEP 15: GET MY CAR INVESTMENTS
# =============================================================
print_step "15" "GET MY CAR INVESTMENTS (shares owned)"

RESPONSE=$(curl -s -X GET "$BASE_URL/cars/my-investments" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_result "$RESPONSE"

# =============================================================
# STEP 16: GET WALLET BALANCE
# =============================================================
print_step "16" "GET WALLET BALANCE"

RESPONSE=$(curl -s -X GET "$BASE_URL/wallet/balance" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_result "$RESPONSE"

# =============================================================
# STEP 17: GET TRANSACTION HISTORY
# =============================================================
print_step "17" "GET TRANSACTION HISTORY"

RESPONSE=$(curl -s -X GET "$BASE_URL/wallet/transactions?page=1&per_page=20" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_result "$RESPONSE"

# =============================================================
# STEP 18: SUBMIT WITHDRAWAL REQUEST
# =============================================================
print_step "18" "SUBMIT WITHDRAWAL REQUEST (100 EGP via Instapay)"

RESPONSE=$(curl -s -X POST "$BASE_URL/wallet/withdrawal-request" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "amount": 100,
    "payment_method": "instapay",
    "account_details": "01012345678"
  }')

print_result "$RESPONSE"

WITHDRAWAL_ID=$(echo "$RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('data',{}).get('request_id', d.get('data',{}).get('id','')))
" 2>/dev/null)

# =============================================================
# STEP 19: GET PENDING WITHDRAWAL
# =============================================================
print_step "19" "GET PENDING WITHDRAWAL REQUEST"

RESPONSE=$(curl -s -X GET "$BASE_URL/wallet/pending-request" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_result "$RESPONSE"

# =============================================================
# STEP 20: GET WITHDRAWAL HISTORY
# =============================================================
print_step "20" "GET WITHDRAWAL REQUESTS HISTORY"

RESPONSE=$(curl -s -X GET "$BASE_URL/wallet/withdrawal-requests?page=1&per_page=20" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_result "$RESPONSE"

# =============================================================
# STEP 21: CANCEL WITHDRAWAL REQUEST
# =============================================================
if [ -n "$WITHDRAWAL_ID" ] && [ "$WITHDRAWAL_ID" != "" ]; then
    print_step "21" "CANCEL WITHDRAWAL REQUEST (ID: $WITHDRAWAL_ID)"

    RESPONSE=$(curl -s -X POST "$BASE_URL/wallet/cancel-request/$WITHDRAWAL_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    print_result "$RESPONSE"
else
    print_step "21" "SKIP - No withdrawal to cancel"
fi

# =============================================================
# STEP 22: UPDATE PROFILE
# =============================================================
print_step "22" "UPDATE PROFILE"

RESPONSE=$(curl -s -X PUT "$BASE_URL/user/profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"name\": \"$TEST_NAME Updated\",
    \"phone\": \"01098765432\"
  }")

print_result "$RESPONSE"

# =============================================================
# STEP 23: SUBMIT KYC DATA
# =============================================================
print_step "23" "SUBMIT KYC DATA"

RESPONSE=$(curl -s -X POST "$BASE_URL/user/kyc" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "phone": "01012345678",
    "national_id": "29001011234567",
    "address": "123 Test Street, Cairo",
    "date_of_birth": "1990-01-01",
    "nationality": "Egyptian",
    "occupation": "Engineer"
  }')

print_result "$RESPONSE"

# =============================================================
# STEP 24: REFRESH TOKEN
# =============================================================
print_step "24" "REFRESH ACCESS TOKEN"

RESPONSE=$(curl -s -X POST "$BASE_URL/auth/refresh" \
  -H "Authorization: Bearer $REFRESH_TOKEN")

print_result "$RESPONSE"

NEW_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('access_token',d.get('access_token','')))" 2>/dev/null)

if [ -n "$NEW_TOKEN" ] && [ "$NEW_TOKEN" != "" ]; then
    echo -e "${GREEN}New Access Token: ${NEW_TOKEN:0:50}...${NC}"
fi

# =============================================================
# STEP 25: VERIFY PROFILE AFTER ALL UPDATES
# =============================================================
print_step "25" "FINAL PROFILE CHECK"

TOKEN_TO_USE="${NEW_TOKEN:-$ACCESS_TOKEN}"

RESPONSE=$(curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN_TO_USE")

print_result "$RESPONSE"

# =============================================================
# DONE
# =============================================================
echo ""
echo "============================================================="
echo -e "${GREEN}ALL TESTS COMPLETED!${NC}"
echo "============================================================="
echo ""
echo -e "${YELLOW}Summary of test credentials:${NC}"
echo "  Email:    $TEST_EMAIL"
echo "  Password: $TEST_PASSWORD"
echo "  Token:    ${ACCESS_TOKEN:0:50}..."
echo ""
echo -e "${YELLOW}What to test next from Admin panel:${NC}"
echo "  1. Go to http://20.20.21.41:5001/admin/dashboard"
echo "  2. Approve/Reject the investment request"
echo "  3. Check if push notification was sent"
echo "  4. Distribute monthly payouts"
echo "  5. Approve/Reject the withdrawal request"
echo ""
echo -e "${YELLOW}To test from your phone:${NC}"
echo "  Base URL: $BASE_URL"
echo "  Add header: Authorization: Bearer $ACCESS_TOKEN"
echo "============================================================="

# Cleanup temp files
rm -f /tmp/test_id_front.jpg /tmp/test_id_back.jpg /tmp/test_proof.jpg
