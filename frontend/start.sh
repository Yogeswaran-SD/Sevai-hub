#!/bin/bash
# Start script for SevaiHub frontend

set -e

echo "Starting SevaiHub Frontend..."

# Install dependencies
echo "Installing dependencies..."
npm ci

# Build the application
echo "Building Vite application..."
npm run build

# Start nginx
echo "Starting Nginx server..."
nginx -g "daemon off;"
