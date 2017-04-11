for code in `cat scripts/mothers.txt`
do
	echo $code
	python main.py $code &
	sleep 1
done
wait
