#include "MyNum.h"
#include <iostream>
#include <cassert>
#include <cstdlib>

MyNum::MyNum(){
	this->den = 0;
	this->num = 1;
}

MyNum::MyNum(long long int i){
	this->den = i;
	this->num = 1;
}

MyNum::MyNum(long long int _den, long long int _num){
	assert(_num > 0);
	this->den = _den;
	this->num = _num;
	this->abbr();
}

MyNum MyNum::operator-(){
	MyNum n(-this->den, this->num);
	return n;
}

MyNum& MyNum::operator=(const MyNum& _n){
	this->den = _n.den;
	this->num = _n.num;
	return *this;
}

MyNum MyNum::operator+(const MyNum& _n){
	long long int nden, nnum;
	nden = this->den * _n.num + this->num * _n.den;
	nnum = this->num * _n.num;
	return MyNum(nden, nnum);
}

MyNum MyNum::operator-(const MyNum& _n){
	long long int nden, nnum;
	nden = this->den * _n.num - this->num * _n.den;
	nnum = this->num * _n.num;
	return MyNum(nden, nnum);
}

MyNum MyNum::operator*(const MyNum& _n){
	long long int nden, nnum;
	nden = this->den * _n.den;
	nnum = this->num * _n.num;
	return MyNum(nden, nnum);
}

MyNum MyNum::operator/(const MyNum& _n){
	long long int nden, nnum;
	assert(_n.den != 0);
	nden = this->den * _n.num;
	nnum = this->num * _n.den;
	return MyNum(nden, nnum);
}

bool MyNum::operator==(const MyNum& _n){
	return (this->den == _n.den) && (this->num == _n.num);
}

bool MyNum::operator!=(const MyNum& _n){
	return !(*this == _n);
}

bool MyNum::operator<(const MyNum& _n){
	MyNum tmp = *this - _n;
	return tmp.den < 0;
}

bool MyNum::operator>(const MyNum& _n){
	MyNum tmp = *this - _n;
	return tmp.den > 0;
}

bool MyNum::operator<=(const MyNum& _n){
	MyNum tmp = *this - _n;
	return tmp.den <= 0;
}

bool MyNum::operator>=(const MyNum& _n){
	MyNum tmp = *this - _n;
	return tmp.den >= 0;
}

std::ostream& operator<<(std::ostream& out, const MyNum& _n){
	if(_n.num==1)
		out << _n.den;
	else
		out << _n.den << "/" << _n.num;
	return out;
}

double MyNum::toDouble(){
	double d = this->den;
	return d / this->num;
}

void MyNum::abbr(){
	bool sgn = this->den * this->num > 0;
	long long int n1, n2, tmp;
	n1 = abs(this->den);
	n2 = abs(this->num);
	while(n1 % n2 != 0){
		n1 %= n2;
		tmp = n2;
		n2 = n1;
		n1 = tmp;
	}
	this->den /= n2;
	this->num /= n2;
	this->den = sgn ? abs(this->den) : -abs(this->den);
	this->num = abs(this->num);
}

