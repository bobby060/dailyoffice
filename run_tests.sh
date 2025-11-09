#!/bin/bash
# Test runner script for Daily Office Prayer Generator

echo "=================================="
echo "Daily Office - Running Tests"
echo "=================================="
echo ""

# Run tests with verbose output
python3 -m unittest discover -s tests -p "test_*.py" -v

# Capture exit code
EXIT_CODE=$?

echo ""
echo "=================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "✗ Some tests failed"
fi
echo "=================================="

exit $EXIT_CODE
