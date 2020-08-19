user_interrupt(){
	jobs
   kill %1
   exit 0
}

trap user_interrupt SIGINT
trap user_interrupt SIGTSTP

tail -f logs/latest.log &

while [ true ] ; do
   read cmd
   echo "$cmd" > ./serv-input
done
