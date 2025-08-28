#!/bin/bash

# 🚀 AWS Gateway Testing - Local Development Starter
echo "🚀 Starting AWS Gateway Testing Project..."

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the AWS_gateway directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install from https://nodejs.org"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install Node.js"
    exit 1
fi

echo "✅ Prerequisites satisfied!"

# Start frontend development
echo "📦 Installing frontend dependencies..."
cd frontend

if [ ! -d "node_modules" ]; then
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo "🎯 Starting development server..."
echo ""
echo "📝 Instructions:"
echo "1. The frontend will start at http://localhost:3000"
echo "2. Update the API URL in the app to your deployed Lambda URL"
echo "3. Follow AWS_SETUP_GUIDE.md to deploy your backend"
echo ""
echo "🔗 Quick Links:"
echo "   Frontend: http://localhost:3000"
echo "   Setup Guide: ../AWS_SETUP_GUIDE.md"
echo ""

npm run dev