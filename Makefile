CC=g++

STH : MyNum.o main.o
	g++ -o STH MyNum.o main.o -O2 -ljsoncpp `pkg-config --cflags --libs opencv`

MyNum.o : MyNum.h MyNum.cpp
	g++ -c -Wno-deprecated-declarations MyNum.cpp -O2 -ljsoncpp

main.o : main.cpp MyNum.h
	g++ -c main.cpp -O2 -ljsoncpp

clean :
	rm MyNum.o main.o

