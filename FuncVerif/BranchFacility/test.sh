echo ">>> Running Verification (Actual Logic simulation)"
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
