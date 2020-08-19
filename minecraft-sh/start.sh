

start_serv() {

	mkfifo ./serv-input
	tail -f ./serv-input | java -jar paper-4.jar nogui > /dev/null
	rm ./serv-input

}

start_serv &
