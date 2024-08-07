#include "MyNum.h"
#include "data.h"
#include <iostream>

int main(int argc, char** argv){
	std::cout<<"Hello"<<std::endl;
	MyNum n1(1);
	MyNum n2(4,3);
	MyNum n3(2,3);
	std::cout<<n1<<std::endl;
	std::cout<<n2<<std::endl;
	std::cout<<n3<<std::endl;
	std::cout<<n1+n2<<std::endl;
	std::cout<<n1+n2+n3<<std::endl;
	std::cout<<n2*n2<<std::endl;
	std::cout<<n1-n2<<std::endl;
	std::cout<<n1/n2<<std::endl;
	std::cout<<-n1<<std::endl;
	Data dt;
	cout << "input instance: " << argv[1] << endl;
	dt.input = argv[1];
	dt.ReadData();
	return 0;
}
