#include "MyNum.h"
#include <iostream>

int main(){
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
	return 0;
}
