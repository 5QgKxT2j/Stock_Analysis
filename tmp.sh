for code in `cat code.txt | head -n 100`
do
	echo $code
	python correlation.py $code > ~/correlation/$core.txt &
done
wait
