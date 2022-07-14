echo ">>> Running Verification (Actual Logic simulation)"
make
# Counts how many line contains a failure
fails=`grep "failure" results.xml | wc -l`
if ! [ $fails -eq 0 ]
then
    echo ">>> Error: Verification failed"
    exit 1
fi

echo ">>> Verification PASSED"
exit 0
