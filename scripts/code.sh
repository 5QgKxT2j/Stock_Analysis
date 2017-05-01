for code in `cat scripts/code.txt | head -500`
do
	echo $code
	python main.py $code &
	sleep 10
done
wait
