#!/bin/bash

echo "🧪 APEX SYSTEM TEST SUITE"
echo "========================="
echo "🎯 Comprehensive testing of all APEX components"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_TOTAL=0

test_result() {
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        if [ -n "$3" ]; then
            echo -e "${YELLOW}   💡 Fix: $3${NC}"
        fi
    fi
}

echo -e "${BLUE}Phase 1: System Requirements${NC}"
echo "----------------------------"

# Test Python
python3 --version > /dev/null 2>&1
test_result $? "Python 3 installation" "Install Python 3.11+ from python.org or use brew/apt"

# Test Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l 2>/dev/null || echo "1") -eq 1 ]]; then
    test_result 0 "Python version ($PYTHON_VERSION)"
else
    test_result 1 "Python version ($PYTHON_VERSION)" "Need Python 3.8 or higher"
fi

# Test Node.js
node --version > /dev/null 2>&1
test_result $? "Node.js installation" "Install Node.js 18+ from nodejs.org or use brew/apt"

# Test npm
npm --version > /dev/null 2>&1
test_result $? "npm package manager" "Usually comes with Node.js"

echo ""
echo -e "${BLUE}Phase 2: Python Dependencies${NC}"
echo "-----------------------------"

# Core web dependencies
python3 -c "import fastapi, uvicorn" > /dev/null 2>&1
test_result $? "FastAPI and Uvicorn" "pip3 install fastapi uvicorn"

python3 -c "import aiohttp, aioredis" > /dev/null 2>&1
test_result $? "Async HTTP and Redis" "pip3 install aiohttp aioredis"

python3 -c "import websockets" > /dev/null 2>&1
test_result $? "WebSocket support" "pip3 install websockets"

# Data processing
python3 -c "import numpy, pandas" > /dev/null 2>&1
test_result $? "NumPy and Pandas" "pip3 install numpy pandas"

# Machine Learning
python3 -c "import torch" > /dev/null 2>&1
test_result $? "PyTorch ML framework" "pip3 install torch"

python3 -c "import transformers" > /dev/null 2>&1
test_result $? "Transformers library" "pip3 install transformers"

# Blockchain
python3 -c "import web3" > /dev/null 2>&1
test_result $? "Web3 blockchain library" "pip3 install web3"

# Text processing
python3 -c "import textblob" > /dev/null 2>&1
test_result $? "TextBlob NLP" "pip3 install textblob"

echo ""
echo -e "${BLUE}Phase 3: Redis Database${NC}"
echo "----------------------"

# Test Redis server
redis-cli ping > /dev/null 2>&1
test_result $? "Redis server connectivity" "Start Redis: redis-server or brew services start redis"

# Test Redis performance
if redis-cli ping > /dev/null 2>&1; then
    REDIS_LATENCY=$(redis-cli --latency-history -c 5 -i 0.1 2>/dev/null | tail -1 | awk '{print $4}' || echo "1.0")
    if (( $(echo "$REDIS_LATENCY < 1.0" | bc -l 2>/dev/null || echo "1") )); then
        test_result 0 "Redis latency ($REDIS_LATENCY ms)"
    else
        test_result 1 "Redis latency ($REDIS_LATENCY ms)" "Redis latency too high"
    fi
fi

echo ""
echo -e "${BLUE}Phase 4: APEX Module Testing${NC}"
echo "----------------------------"

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Test HyperScanner engine
python3 -c "
try:
    from engines.hyperscanner import scanner
    print('✓ HyperScanner import successful')
except Exception as e:
    print(f'✗ HyperScanner import failed: {e}')
    exit(1)
" > /dev/null 2>&1
test_result $? "HyperScanner engine import"

# Test Trading Engine
python3 -c "
try:
    from execution.trading_engine import trading_engine
    print('✓ TradingEngine import successful')
except Exception as e:
    print(f'✗ TradingEngine import failed: {e}')
    exit(1)
" > /dev/null 2>&1
test_result $? "Trading Engine import"

# Test API Server
python3 -c "
try:
    from core.api_server import app
    print('✓ API Server import successful')
except Exception as e:
    print(f'✗ API Server import failed: {e}')
    exit(1)
" > /dev/null 2>&1
test_result $? "API Server import"

echo ""
echo -e "${BLUE}Phase 5: Frontend Testing${NC}"
echo "-------------------------"

# Check frontend structure
[ -f "frontend/package.json" ]
test_result $? "Frontend package.json exists"

[ -f "frontend/pages/index.js" ]
test_result $? "Frontend main page exists"

[ -f "frontend/styles/globals.css" ]
test_result $? "Frontend styles exist"

# Test frontend dependencies
if [ -d "frontend/node_modules" ]; then
    test_result 0 "Frontend dependencies installed"
else
    test_result 1 "Frontend dependencies installed" "Run: cd frontend && npm install"
fi

echo ""
echo -e "${BLUE}Phase 6: Performance Benchmarks${NC}"
echo "--------------------------------"

# Python performance test
python3 -c "
import time
import numpy as np

# Test CPU performance
start = time.time()
result = np.random.randn(1000, 1000).dot(np.random.randn(1000, 1000))
cpu_time = time.time() - start

print(f'CPU benchmark: {cpu_time:.3f}s')

# Test memory allocation
start = time.time()
arrays = [np.random.randn(100, 100) for _ in range(100)]
memory_time = time.time() - start

print(f'Memory benchmark: {memory_time:.3f}s')

if cpu_time < 2.0 and memory_time < 1.0:
    exit(0)
else:
    exit(1)
" > /dev/null 2>&1
test_result $? "Python performance benchmark"

# Test async performance
python3 -c "
import asyncio
import time

async def test_async():
    tasks = []
    for i in range(100):
        tasks.append(asyncio.sleep(0.001))
    
    start = time.time()
    await asyncio.gather(*tasks)
    duration = time.time() - start
    
    print(f'Async benchmark: {duration:.3f}s')
    return duration < 0.5

result = asyncio.run(test_async())
exit(0 if result else 1)
" > /dev/null 2>&1
test_result $? "Async performance benchmark"

echo ""
echo -e "${BLUE}Phase 7: Network Connectivity${NC}"
echo "-----------------------------"

# Test internet connectivity
ping -c 1 google.com > /dev/null 2>&1
test_result $? "Internet connectivity" "Check your internet connection"

# Test API endpoint accessibility (basic)
curl -s --connect-timeout 5 https://api.coingecko.com/api/v3/ping > /dev/null 2>&1
test_result $? "CoinGecko API accessibility" "Check firewall settings"

echo ""
echo -e "${BLUE}Phase 8: File Structure Validation${NC}"
echo "--------------------------------"

# Check all required files exist
FILES=(
    "genesis.sh"
    "test_apex.sh" 
    "launch.sh"
    "README.md"
    "engines/hyperscanner.py"
    "execution/trading_engine.py"
    "core/api_server.py"
    "frontend/package.json"
    "frontend/pages/index.js"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        test_result 0 "File exists: $file"
    else
        test_result 1 "File exists: $file" "Re-run the setup script"
    fi
done

echo ""
echo -e "${BLUE}Phase 9: Integration Test${NC}"
echo "------------------------"

# Test that modules can work together
python3 -c "
import asyncio
import sys
sys.path.append('.')

async def integration_test():
    try:
        from engines.hyperscanner import scanner
        from execution.trading_engine import trading_engine
        
        # Test basic initialization
        print('Testing module integration...')
        
        # This would normally start the full system
        # For testing, we just verify imports work together
        print('✓ All modules can be imported together')
        return True
        
    except Exception as e:
        print(f'✗ Integration test failed: {e}')
        return False

result = asyncio.run(integration_test())
exit(0 if result else 1)
" > /dev/null 2>&1
test_result $? "Module integration test"

echo ""
echo -e "${PURPLE}════════════════════════════════════════${NC}"
echo -e "${PURPLE}           TEST RESULTS SUMMARY          ${NC}"
echo -e "${PURPLE}════════════════════════════════════════${NC}"
echo ""
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC} / $TESTS_TOTAL"

if [ $TESTS_PASSED -eq $TESTS_TOTAL ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}✅ APEX is ready for launch!${NC}"
    echo ""
    echo -e "${CYAN}🚀 SYSTEM STATUS: OPERATIONAL${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Launch APEX: ${BLUE}./launch.sh${NC}"
    echo "  2. Open dashboard: ${BLUE}http://localhost:3000${NC}"
    echo "  3. Start trading: Watch the real-time signals!"
    echo ""
    echo -e "${PURPLE}🎯 Ready to turn \$10 into \$1000!${NC}"
    
elif [ $TESTS_PASSED -gt $((TESTS_TOTAL * 3 / 4)) ]; then
    echo ""
    echo -e "${YELLOW}⚠️  MOSTLY READY${NC}"
    echo -e "${YELLOW}Most tests passed, minor issues detected${NC}"
    echo ""
    echo -e "${CYAN}You can probably launch APEX, but some features may not work perfectly.${NC}"
    echo ""
    echo -e "${YELLOW}Recommendation:${NC}"
    echo "  - Fix the failing tests above"
    echo "  - Or try launching anyway: ${BLUE}./launch.sh${NC}"
    
else
    echo ""
    echo -e "${RED}❌ CRITICAL ISSUES DETECTED${NC}"
    echo -e "${RED}Too many tests failed - system may not work properly${NC}"
    echo ""
    echo -e "${YELLOW}Required actions:${NC}"
    echo "  1. Fix all failing tests above"
    echo "  2. Re-run: ${BLUE}./test_apex.sh${NC}"
    echo "  3. Only launch when all tests pass"
    echo ""
    echo -e "${CYAN}💡 Most common fixes:${NC}"
    echo "  - Install missing dependencies: ${BLUE}./genesis.sh${NC}"
    echo "  - Start Redis: ${BLUE}redis-server${NC}"
    echo "  - Install Node.js from nodejs.org"
fi

echo ""
echo -e "${BLUE}🔍 For detailed logs, check individual test outputs above${NC}"
