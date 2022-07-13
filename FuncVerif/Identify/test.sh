echo ">>> Running Python unit tests (Not Logic design)"
python3 utils.py
# If it fails, you have a problem in your verification code, not in your design
if ! [ $? -eq 0 ]
then
    echo ">>> Error: You have a problem in your python code"
    exit 1
fi

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
