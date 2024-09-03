#include "MyNum.h"
#include <cassert>
#include <cstdlib>
#include <cmath>

constexpr double EPS = 10e-6;
constexpr long long int LIM = 100000000;
constexpr int LIMDOUBLE = 30;

BigNum::BigNum() {
	sgn = true;
	nums.push_back(0);
}

BigNum::BigNum(long long int _n) {
	sgn = _n >= 0;
	if (_n == 0) nums.push_back(0);
	else {
		_n = llabs(_n);
		while (_n > 0) {
			nums.push_back(_n % LIM);
			_n /= LIM;
		}
	}
}

BigNum::BigNum(const BigNum& _num) {
	this->sgn = _num.sgn;
	this->nums = _num.nums;
}

BigNum BigNum::operator-() const{
	BigNum _n = *this;
	_n.sgn = !sgn;
	return _n;
}

BigNum& BigNum::operator=(const BigNum& _n) {
	this->sgn = _n.sgn;
	this->nums = _n.nums; //
	return *this;
}

BigNum BigNum::operator+(const BigNum& _n) {
	BigNum res;
	res.nums.clear();
	if (sgn == _n.sgn) {
		res.sgn = sgn;
		int s = nums.size() < _n.nums.size() ? _n.nums.size() : nums.size();
		res.nums = std::vector<unsigned long long int>(s, 0);
		for(int i = 0; i < s; i++) {
			if (i < nums.size()) res.nums[i] += nums[i];
			if (i < _n.nums.size()) res.nums[i] += _n.nums[i];
			if (res.nums[i] >= LIM) {
				res.nums[i] -= LIM;
				if (i == s - 1) res.nums.push_back(1);
				else res.nums[i + 1] += 1;
			}
		}
	}
	else {
		if (*this == -_n) {
			res.nums.push_back(0);
			res.sgn = true;
		}
		else {
			const BigNum* posNum = nullptr, * negNum = nullptr;
			if (this->sgn) {
				posNum = this;
				negNum = &_n;
			}
			else {
				negNum = this;
				posNum = &_n;
			}
			int s = nums.size() < _n.nums.size() ? _n.nums.size() : nums.size();
			res.nums = std::vector<unsigned long long int>(s, 0);
			const BigNum* greAbsNum = nullptr, * lessAbsNum = nullptr;
			
			if (posNum->nums.size() > negNum->nums.size()) {
				res.sgn = true;
				greAbsNum = posNum;
				lessAbsNum = negNum;
			}
			else if (posNum->nums.size() < negNum->nums.size()) {
				res.sgn = false;
				greAbsNum = negNum;
				lessAbsNum = posNum;
			}
			else {
				for (int i = 0; i < s; i++) {
					if (posNum->nums[i] > negNum->nums[i]) {
						res.sgn = true;
						greAbsNum = posNum;
						lessAbsNum = negNum;
						break;
					}
					else if (posNum->nums[i] < negNum->nums[i]) {
						res.sgn = false;
						greAbsNum = negNum;
						lessAbsNum = posNum;
						break;
					}
				}
			}

			for (int i = 0; i < s; i++) {
				if (i < greAbsNum->nums.size()) res.nums[i] += greAbsNum->nums[i];
				if (i < lessAbsNum->nums.size()) res.nums[i] -= lessAbsNum->nums[i];
				if (res.nums[i] < 0) {
					res.nums[i] += LIM;
					res.nums[i + 1] -= 1;
				}
			}
			// 0 제거
			auto it = res.nums.end();
			while (it != res.nums.begin()){
				it--;
				if (*it == 0)
					it = res.nums.erase(it);
				else {
					break;
				}
			}
		}
	}
	return res;
}

BigNum BigNum::operator-(const BigNum& BN) {
	return (*this) + (-BN);
}

BigNum BigNum::operator*(const BigNum& BN) {
	BigNum res;
	res.nums.clear();
	if (this->isZero() || BN.isZero()) {
		res.nums.push_back(0);
	}
	else {
		if (this->sgn == BN.sgn) {
			res.sgn = true;
		}
		else {
			res.sgn = false;
		}
		res.nums = std::vector<unsigned long long int>(this->nums.size()+ BN.nums.size(), 0);
		for (int i = 0; i < this->nums.size(); i++) {
			for (int j = 0; j < BN.nums.size(); j++) {
				res.nums[i + j] += this->nums[i] * BN.nums[j];
				if (res.nums[i + j] >= LIM) {
					res.nums[i + j + 1] += res.nums[i + j] / LIM;
					res.nums[i + j] %= LIM;
				}
			}
		}

		// 0 제거
		auto it = res.nums.end();
		while (it != res.nums.begin()){
			it--;
			if (*it == 0)
				it = res.nums.erase(it);
			else {
				break;
			}
		}
	}
	return res;
}

bool BigNum::operator==(const BigNum& BN) {
	if (this->sgn == BN.sgn && this->nums.size() == BN.nums.size()) {
		bool flag = true;
		for (size_t i = 0; i < this->nums.size(); i++) {
			if (this->nums[i] != BN.nums[i]) {
				flag = false;
				break;
			}
		}
		return flag;
	}
	else {
		return false;
	}
}
bool BigNum::operator!=(const BigNum& BN) {
	if (this->sgn != BN.sgn || this->nums.size() != BN.nums.size()) {
		return true;
	}
	else {
		bool flag = false;
		for (size_t i = 0; i < this->nums.size(); i++) {
			if (this->nums[i] != BN.nums[i]) {
				flag = true;
				break;
			}
		}
		return flag;
	}
}
bool BigNum::operator<(const BigNum& BN) {
	BigNum tmp(*this - BN);
	if (tmp.isZero()) return false;
	else {
		return !tmp.sgn;
	}
}
bool BigNum::operator>(const BigNum& BN) {
	BigNum tmp(*this - BN);
	if (tmp.isZero()) return false;
	else {
		return tmp.sgn;
	}
}
bool BigNum::operator<=(const BigNum& BN) {
	BigNum tmp(*this - BN);
	if (tmp.isZero()) return true;
	else {
		return !tmp.sgn;
	}
}
bool BigNum::operator>=(const BigNum& BN) {
	BigNum tmp(*this - BN);
	if (tmp.isZero()) return true;
	else {
		return tmp.sgn;
	}
}
std::ostream& operator<<(std::ostream& out, const BigNum& _n) {
	for (auto it = _n.nums.rbegin(); it != _n.nums.rend(); it++) {
		out << *it;
	}
	return out;
}

BigNum BigNum::abs() {
	BigNum res(*this);
	res.sgn = true;
	return res;
}

bool BigNum::isOne() const {
	if (this->nums.size() == 1 && this->nums.front() == 1) {
		return true;
	}
	else {
		return false;
	}
}

bool BigNum::isZero() const {
	if (this->nums.size() == 1 && this->nums.front() == 0) {
		return true;
	}
	else {
		return false;
	}
}

std::pair<long double, int> BigNum::toDouble() {
	long double res_first = 0;
	int res_second = 0;
	int range = this->nums.size();
	if (range > LIMDOUBLE) { // 38까지 괜찮음
		res_second = range - LIMDOUBLE;
		range = LIMDOUBLE;
	}
	for (int i = 0; i < range; i++) {
		long double tmp = this->nums[i + res_second];
		res_first += tmp * std::pow(LIM,i);
	}
	return std::make_pair(res_first, res_second);
}

void BigNum::plusOneIdx(int idx) {
	// 예외 처리
	this->nums[idx]++;
	for (int i = idx; i < this->nums.size(); i++) {
		if (this->nums[i] == LIM) {
			this->nums[i] = 0;
			if (i == this->nums.size() - 1) {
				this->nums.push_back(1);
			}
			else {
				this->nums[i + 1]++;
			}
		}
		else {
			break;
		}
	}
}

void BigNum::divideByGCD(const BigNum& BN) {
	BigNum tmpA(*this);
	BigNum tmpB(BN);
	BigNum tmpC;

	// 현재 BigNum과 BN 둘 다 양수라고 가정
	while (!tmpA.isZero()) {
		tmpA = tmpA - tmpB;
		tmpC.plusOneIdx(0);
	}
	this->nums.clear();
	this->nums = tmpC.nums;
}

MyNum::MyNum(){
	this->num = BigNum(0);
	this->den = BigNum(1);
}

MyNum::MyNum(long long int i){
	this->num = BigNum(i);
	this->den = BigNum(1);
}

MyNum::MyNum(long long int _num, long long int _den){
	assert(_den != 0);
	this->num = BigNum(_num);
	this->den = BigNum(_den);
	this->abbr();
}

MyNum::MyNum(BigNum _num, BigNum _den) {
	assert(_den.isZero() != true);
	this->num = _num;
	this->den = _den;
	this->abbr();
}

MyNum::MyNum(const MyNum& _num) {
	assert(_num.den.isZero() != true);
	this->num = _num.num;
	this->den = _num.den;
	this->abbr();
}

MyNum MyNum::operator-() const {
	MyNum ret(-this->num, this->den);
	return ret;
}

MyNum& MyNum::operator=(const MyNum& _n){
	this->num = _n.num;
	this->den = _n.den;
	return *this;
}

MyNum MyNum::operator+(const MyNum& _n){
	if (this->den.isOne()) {
		if (_n.den.isOne()) {
			BigNum retNum(this->num + _n.num);
			return MyNum(retNum, this->den);
		}
		else {
			BigNum retNum(this->num * _n.den + _n.num);
			return MyNum(retNum, _n.den);
		}
	}
	else {
		if (_n.den.isOne()) {
			BigNum retNum(this->num + this->den * _n.num);
			return MyNum(retNum, this->den);
		}
		else {
			BigNum retNum(this->num * _n.den + this->den * _n.num);
			BigNum retDen(this->den * _n.den);
			return MyNum(retNum, retDen);
		}
	}
}

MyNum MyNum::operator-(const MyNum& _n){
	if (this->den.isOne()) {
		if (_n.den.isOne()) {
			BigNum retNum(this->num - _n.num);
			return MyNum(retNum, this->den);
		}
		else {
			BigNum retNum(this->num * _n.den - _n.num);
			return MyNum(retNum, _n.den);
		}
	}
	else {
		if (_n.den.isOne()) {
			BigNum retNum(this->num - this->den * _n.num);
			return MyNum(retNum, this->den);
		}
		else {
			BigNum retNum(this->num * _n.den - this->den * _n.num);
			BigNum retDen(this->den * _n.den);
			return MyNum(retNum, retDen);
		}
	}
}

MyNum MyNum::operator*(const MyNum& _n){
	BigNum retNum(this->num * _n.num);
	BigNum retDen(this->den * _n.den);
//	std::cout<<this->den<<"/"<<this->num<<" * "<<_n.den<<"/"<<_n.num<<" = "<<nden<<"/"<<nnum<<std::endl;
	return MyNum(retNum, retDen);
}

MyNum MyNum::operator/(const MyNum& _n){
	assert(_n.num.isZero() != true);
	BigNum retNum(this->num * _n.den);
	BigNum retDen(this->den * _n.num);
	return MyNum(retNum, retDen);
}

bool MyNum::operator==(const MyNum& _n){
	return (this->num == _n.num) && (this->den == _n.den);
}

bool MyNum::operator!=(const MyNum& _n){
	return (this->num != _n.num) || (this->den != _n.den);
}

bool MyNum::operator<(const MyNum& _n){
	MyNum tmp = *this - _n;
	return tmp.num < 0;
}

bool MyNum::operator>(const MyNum& _n){
	MyNum tmp = *this - _n;
	return tmp.num > 0;
}

bool MyNum::operator<=(const MyNum& _n){
	MyNum tmp = *this - _n;
	return tmp.num <= 0;
}

bool MyNum::operator>=(const MyNum& _n){
	MyNum tmp = *this - _n;
	return tmp.num >= 0;
}

std::ostream& operator<<(std::ostream& out, const MyNum& _n){
	if (_n.den.isOne())
		out << _n.num;
	else
		out << "\"" << _n.num << "/" << _n.den << "\"";
	return out;
}

// 수정 필요
long double MyNum::toDouble(){
	std::pair<long double, int> nd = this->num.toDouble();
	std::pair<long double, int> dd = this->den.toDouble();

	long double d = nd.first / dd.first;

	if (nd.second - dd.second > 0) {
		d = d * std::pow(LIM, nd.second - dd.second);
	}
	else if (nd.second - dd.second < 0) {
		d = d / std::pow(LIM, dd.second - nd.second);
	}

	if (this->num.sgn == this->den.sgn) {
		return d;
	}
	else {
		return -d;
	}
}

// 수정 필요
void MyNum::abbr() {
	bool newSgn = (this->num.sgn == this->den.sgn);

	this->num.sgn = true;
	this->den.sgn = true;
	BigNum tmpA(this->num);
	BigNum tmpB(this->den);
	BigNum* ptr0 = &tmpA;
	BigNum* ptr1 = &tmpB;
	BigNum tmpC;
	tmpC = *ptr0;

	tmpC = *ptr0;
	while (!tmpC.isZero()) {
		tmpC = *ptr0;
		while (!tmpC.isZero() != !tmpC.sgn) {
			*ptr0 = tmpC;
			/*
			BigNum tmpD(tmpC - *ptr1);
			tmpC = tmpD;
			*/
			tmpC = tmpC - *ptr1;
		}
		BigNum* tmpPtr = ptr0;
		ptr0 = ptr1;
		ptr1 = tmpPtr;
	}

	// ptr0 is GCD 
	this->num.divideByGCD(*ptr0);
	this->den.divideByGCD(*ptr0);
	this->num.sgn = newSgn;
	this->den.sgn = true;
}
