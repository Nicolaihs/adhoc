#!/bin/bash

# Check if a query parameter is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <query>"
  exit 1
fi

# Define the URL with the query parameter
URL="https://ordnet.dk/ddo/ordbog?query=$1"

# Use curl to fetch headers and grep for the X-Cache header
X_CACHE=$(curl -sI "$URL" | grep -i "X-Cache")

# Check if the X-Cache header was found
if [ -n "$X_CACHE" ]; then
  echo "Cache status for '$URL': $X_CACHE"
else
  echo "X-Cache header not found. Please check the Varnish configuration or the URL."
fi