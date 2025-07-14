#!/bin/bash

echo "🌐 Opening APEX Dashboard"
echo "========================"

# Check if the backend is running
if curl -s http://localhost:8000/api/buy-signals > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend not detected on port 8000"
    echo "💡 Make sure you've run: ./launch.sh"
    exit 1
fi

# Check if the frontend is running  
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend not detected on port 3000"
    echo "💡 Make sure you've run: ./launch.sh"
    exit 1
fi

echo ""
echo "🚀 Opening APEX Dashboard..."
echo "📊 URL: http://localhost:3000"
echo ""

# Open dashboard based on OS
if command -v open > /dev/null 2>&1; then
    # macOS
    open http://localhost:3000
elif command -v xdg-open > /dev/null 2>&1; then
    # Linux
    xdg-open http://localhost:3000
elif command -v start > /dev/null 2>&1; then
    # Windows
    start http://localhost:3000
else
    echo "💻 Please manually open: http://localhost:3000"
fi

echo "✅ Dashboard should now be open in your browser!"
echo ""
echo "🎯 What you'll see:"
echo "   • Left panel: Real-time BUY signals (95%+ confidence)"
echo "   • Right panel: Active trading positions"
echo "   • Top bar: Live performance metrics"
echo "   • Real-time updates every 500ms"
echo ""
echo "💰 Happy trading! Target: \$10 → \$1000"
