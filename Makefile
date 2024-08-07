CC=g++

MyNum : data.o MyNum.o main.o
	g++ -o MyNum data.o MyNum.o main.o -O2 -ljsoncpp `pkg-config --cflags --libs opencv`

MyNum.o : MyNum.h MyNum.cpp
	g++ -c -Wno-deprecated-declarations MyNum.cpp -O2 -ljsoncpp

main.o : main.cpp MyNum.h data.h
	g++ -c main.cpp -O2 -ljsoncpp

data.o: data.cpp data.h
	g++ -c -Wno-deprecated-declarations data.cpp -O2 -ljsoncpp

clean :
	rm MyNum data.o main.o MyNum.o
