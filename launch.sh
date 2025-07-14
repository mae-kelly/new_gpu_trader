#!/bin/bash

echo "🚀 LAUNCHING APEX TRADING SYSTEM"
echo "================================="
echo "💰 Mission: \$10 → \$1000 in 24 hours"
echo "⚡ Ultra-aggressive momentum trading"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Set Python path for imports
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo -e "${BLUE}🧹 Cleaning up any existing processes...${NC}"

# Kill any existing APEX processes
pkill -f "python.*api_server.py" 2>/dev/null
pkill -f "npm.*dev" 2>/dev/null
pkill -f "next.*dev" 2>/dev/null

# Wait a moment for cleanup
sleep 2

echo -e "${BLUE}🔴 Checking Redis server...${NC}"

# Check if Redis is running, start if needed
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}Redis not running, starting...${NC}"
    redis-server --daemonize yes --port 6379 --maxmemory 2gb --maxmemory-policy allkeys-lru
    sleep 3
    
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start Redis${NC}"
        echo -e "${YELLOW}💡 Try: brew install redis (macOS) or sudo apt install redis-server (Linux)${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Redis already running${NC}"
fi

echo -e "${BLUE}📡 Starting APEX backend server...${NC}"

# Start the backend API server
cd core
python3 api_server.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Backend server started (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo -e "${YELLOW}💡 Check Python dependencies with: ./test_apex.sh${NC}"
    exit 1
fi

# Test backend API
if curl -s http://localhost:8000/api/buy-signals > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API responding${NC}"
else
    echo -e "${YELLOW}⚠️ Backend API not responding yet (may need more time)${NC}"
fi

echo -e "${BLUE}🌐 Starting APEX frontend dashboard...${NC}"

# Start the frontend development server
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Frontend dependency installation failed${NC}"
        cd ..
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
fi

# Start Next.js development server
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 8

# Check if frontend is running
if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Frontend server started (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}❌ Frontend failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 APEX SYSTEM LAUNCHED SUCCESSFULLY!${NC}"
echo -e "${PURPLE}═══════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}🎯 MISSION CONTROL${NC}"
echo -e "${YELLOW}Target: \$10 → \$1000 in 24 hours${NC}"
echo ""
echo -e "${CYAN}📊 Access Points:${NC}"
echo -e "   Dashboard:  ${BLUE}http://localhost:3000${NC}"
echo -e "   API Server: ${BLUE}http://localhost:8000${NC}"
echo -e "   WebSocket:  ${BLUE}ws://localhost:8000/ws${NC}"
echo ""
echo -e "${CYAN}🔥 System Status:${NC}"
echo -e "   Backend PID:  ${GREEN}$BACKEND_PID${NC}"
echo -e "   Frontend PID: ${GREEN}$FRONTEND_PID${NC}"
echo -e "   Redis:        ${GREEN}Running${NC}"
echo ""
echo -e "${CYAN}💡 Key Features Active:${NC}"
echo -e "   • ${GREEN}Sub-100ms momentum detection${NC}"
echo -e "   • ${GREEN}95%+ confidence AI filtering${NC}"
echo -e "   • ${GREEN}Real-time social sentiment analysis${NC}"
echo -e "   • ${GREEN}Automated risk management${NC}"
echo -e "   • ${GREEN}Whale wallet copy trading${NC}"
echo -e "   • ${GREEN}Multi-modal opportunity classification${NC}"
echo ""
echo -e "${YELLOW}🚨 Trading Strategy:${NC}"
echo -e "   Entry: 9-13% momentum with 95%+ confidence"
echo -e "   Exit: When acceleration stops or profit targets hit"
echo -e "   Risk: Maximum 30% per trade, 20% stop loss"
echo -e "   Speed: Sub-second execution timing"
echo ""
echo -e "${PURPLE}⚡ PRESS CTRL+C TO STOP ALL SERVICES${NC}"
echo ""

# Wait a bit longer for everything to fully start
sleep 5

# Try to open dashboard automatically
if command -v open > /dev/null 2>&1; then
    # macOS
    echo -e "${CYAN}🚀 Opening dashboard automatically...${NC}"
    open http://localhost:3000
elif command -v xdg-open > /dev/null 2>&1; then
    # Linux
    echo -e "${CYAN}🚀 Opening dashboard automatically...${NC}"
    xdg-open http://localhost:3000
else
    echo -e "${YELLOW}💻 Manually open: http://localhost:3000${NC}"
fi

echo ""
echo -e "${GREEN}🎯 APEX IS NOW HUNTING FOR \$1000 OPPORTUNITIES!${NC}"
echo -e "${GREEN}Watch the dashboard for real-time buy/sell signals...${NC}"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down APEX system...${NC}"
    
    # Kill backend
    if kill $BACKEND_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    
    # Kill frontend
    if kill $FRONTEND_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi
    
    # Additional cleanup for any remaining processes
    pkill -f "python.*api_server.py" 2>/dev/null
    pkill -f "npm.*dev" 2>/dev/null
    pkill -f "next.*dev" 2>/dev/null
    
    echo -e "${BLUE}💤 APEX system offline${NC}"
    echo -e "${YELLOW}Thanks for using APEX! 🚀${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Keep the script running and show periodic status
COUNTER=0
while true; do
    sleep 30
    COUNTER=$((COUNTER + 1))
    
    # Check if processes are still running
    if ! ps -p $BACKEND_PID > /dev/null; then
        echo -e "${RED}❌ Backend process died unexpectedly${NC}"
        cleanup
    fi
    
    if ! ps -p $FRONTEND_PID > /dev/null; then
        echo -e "${RED}❌ Frontend process died unexpectedly${NC}"
        cleanup
    fi
    
    # Show periodic status every 5 minutes
    if [ $((COUNTER % 10)) -eq 0 ]; then
        UPTIME=$((COUNTER * 30))
        MINUTES=$((UPTIME / 60))
        echo -e "${CYAN}📊 APEX Status: Running for ${MINUTES} minutes | Dashboard: http://localhost:3000${NC}"
    fi
done
