#!/usr/bin/env bash
set -e

BASE_URL="http://127.0.0.1:5000/api/v1"
ADMIN_EMAIL="admin@hbnb.io"
ADMIN_PASSWORD="admin1234"

AMENITY_NAME="Amenity_$(date +%s)"
UPDATED_AMENITY_NAME="Updated_$(date +%s)"

echo "=============================="
echo " LOGIN AS ADMIN"
echo "=============================="

ADMIN_LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")

echo "$ADMIN_LOGIN_RESPONSE"

ADMIN_TOKEN=$(python3 - <<EOF
import json
data = json.loads('''$ADMIN_LOGIN_RESPONSE''')
print(data.get("access_token", ""))
EOF
)

if [ -z "$ADMIN_TOKEN" ]; then
  echo "Admin login failed"
  exit 1
fi

AUTH_ADMIN="Authorization: Bearer $ADMIN_TOKEN"

echo
echo "=============================="
echo " CREATE AMENITY"
echo "=============================="

CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/amenities/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_ADMIN" \
  -d "{\"name\":\"$AMENITY_NAME\"}")

echo "$CREATE_RESPONSE"

AMENITY_ID=$(python3 - <<EOF
import json
data = json.loads('''$CREATE_RESPONSE''')
print(data.get("id", ""))
EOF
)

if [ -z "$AMENITY_ID" ]; then
  echo "Amenity creation failed"
  exit 1
fi

echo
echo "=============================="
echo " GET AMENITY"
echo "=============================="
curl -s -X GET "$BASE_URL/amenities/$AMENITY_ID"

echo
echo "=============================="
echo " UPDATE AMENITY"
echo "=============================="
curl -s -X PUT "$BASE_URL/amenities/$AMENITY_ID" \
  -H "Content-Type: application/json" \
  -H "$AUTH_ADMIN" \
  -d "{\"name\":\"$UPDATED_AMENITY_NAME\"}"

echo
echo "=============================="
echo " DELETE AMENITY"
echo "=============================="
curl -s -X DELETE "$BASE_URL/amenities/$AMENITY_ID" \
  -H "$AUTH_ADMIN"

echo
echo "=============================="
echo " GET AFTER DELETE"
echo "=============================="
curl -s -X GET "$BASE_URL/amenities/$AMENITY_ID"

echo
echo "=============================="
echo " AMENITIES TEST COMPLETED"
echo "=============================="
