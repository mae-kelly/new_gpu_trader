#!/bin/bash

echo "🧪 APEX TEST"
echo "============"

tests=0
passed=0

check() {
    tests=$((tests + 1))
    if eval "$2" > /dev/null 2>&1; then
        echo "✅ $1"
        passed=$((passed + 1))
    else
        echo "❌ $1"
    fi
}

check "Python" "python3 --version"
check "Node.js" "node --version"
check "API Server" "[ -f 'core/api_server.py' ]"
check "Frontend" "[ -f 'frontend/package.json' ]"
check "Launch Script" "[ -f 'launch.sh' ]"

echo ""
echo "Result: $passed/$tests passed"

if [ $passed -eq $tests ]; then
    echo "🎉 Ready to launch: ./launch.sh"
else
    echo "⚠️ Fix issues above first"
fi
