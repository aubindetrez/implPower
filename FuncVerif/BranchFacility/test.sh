echo ">>> Running Python doctest"
python3 test_BranchFacility.py | tee doctest.log
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

echo ">>> Running Verification"
result_file=results.xml
make

# Check if a result if available
if ! [ -f $result_file ]
then
    echo ">>> Error: Verification failed"
    exit 1
fi

# Counts how many line contains a failure
fails=`grep "failure" $result_file | wc -l`
if ! [ $fails -eq 0 ]
then
    echo ">>> Error: Verification failed"
    exit 1
fi

echo ">>> Verification PASSED"
exit 0
