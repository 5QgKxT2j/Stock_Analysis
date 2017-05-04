#c=0
for i in `cat scripts/code.txt`
do
    while [ `ps -ef | grep "python main.py" | wc -l | awk '{print $1}'` -gt 10 ]
    do
        echo "sleep 1"
		sleep 1
	done
	echo $i
    #sleep 1 &
    python main.py $i &
done
wait