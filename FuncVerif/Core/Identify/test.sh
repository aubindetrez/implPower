echo ">>> Running SystemVerilog based verification"
iverilog -g2012 -Wall -DSIMULATION test_Identify.sv -o sv_bin && ./sv_bin | tee sv.log
if [[ $? != 0 ]]
then
    echo ">>> Error: Verification failed (returned an error)"
    exit 1
fi
fails=`grep "ERROR" sv.log | wc -l`
if ! [ $fails -eq 0 ]
then
    echo ">>> Error: Verification failed (sv.log contains \"ERROR\")"
    exit 1
fi



echo ">>> Running Python based Verification"
make

# Check if a result if available
if ! [ -f "results.xml" ]
then
    echo ">>> Error: Verification failed"
    exit 1
fi

# Counts how many line contains a failure
fails=`grep "failure" results.xml | wc -l`
if ! [ $fails -eq 0 ]
then
    echo ">>> Error: Verification failed"
    exit 1
fi

echo ">>> Verification PASSED"
exit 0
