echo ">>> Running Python unit tests (Not Logic design)"
python3 utils.py
# If it fails, you have a problem in your verification code, not in your design
if ! [ $? -eq 0 ]
then
    echo ">>> Error: You have a problem in your python code"
    exit 1
fi
echo ">>> Python unit tests PASSED"
exit 0
