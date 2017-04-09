for code in `cat mothers.txt`
do
	echo $code
	python main.py $code &
	sleep 10
done
wait
