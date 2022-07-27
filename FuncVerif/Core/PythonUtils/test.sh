echo ">>> Running Python unit tests (Not Logic design)"
python3 utils.py &> >(tee doctest.log) # Redirect both stdout and stderr

# If it fails, you have a problem in your verification code, not in your design
fails=`grep "FAILED" doctest.log | wc -l`
if ! [ $fails -eq 0 ] # Look for any fail
then
    echo ">>> Error: You have a problem in your python code"
    exit 1
fi
echo ">>> Python unit tests PASSED"

echo ">>> Checking doctest's log..."
if ! [ -f "doctest.log" ] # Check a result exists
then
    echo ">>> Error: Python doctest didn't run"
    exit 1
fi
fails=`grep "***Test Failed***" doctest.log | wc -l`
if ! [ $fails -eq 0 ] # Look for any fail
then
    echo ">>> Error: Python doctest failed"
    exit 1
fi
echo ">>> Python doctest PASSED"

exit 0
