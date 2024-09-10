#pragma once
#include <iostream>
#include <vector>
#include <utility>

class BigNum {
public:
	std::vector<unsigned long long int> nums;
	bool sgn;

	BigNum();
	BigNum(long long int);
	BigNum(const BigNum& _num);

	BigNum operator-() const;
	BigNum& operator=(const BigNum&);
	BigNum operator+(const BigNum&);
	BigNum operator-(const BigNum&);
	BigNum operator*(const BigNum&);
	bool operator==(const BigNum&);
	bool operator!=(const BigNum&);
	bool operator<(const BigNum&);
	bool operator>(const BigNum&);
	bool operator<=(const BigNum&);
	bool operator>=(const BigNum&);
	friend std::ostream& operator<<(std::ostream&, const BigNum&);

	BigNum abs();
	bool isOne() const;
	bool isZero() const;
	std::pair<long double, int> toDouble();
	void plusOneIdx(int idx);
	void divideByGCD(const BigNum&);
};

class MyNum {
public:
	BigNum num, den; // numerator, denominator

	MyNum(); // 0
	MyNum(long long int); // 분자만
	MyNum(long long int, long long int); // 분자, 분모
	MyNum(BigNum _num, BigNum _den); // 분자, 분모
	MyNum(const MyNum& _num);

	MyNum operator-() const;
	MyNum& operator=(const MyNum&);
	MyNum operator+(const MyNum&);
	MyNum operator-(const MyNum&);
	MyNum operator*(const MyNum&);
	MyNum operator/(const MyNum&);
	bool operator==(const MyNum&);
	bool operator!=(const MyNum&);
	bool operator<(const MyNum&);
	bool operator>(const MyNum&);
	bool operator<=(const MyNum&);
	bool operator>=(const MyNum&);
	friend std::ostream& operator<<(std::ostream&, const MyNum&);
	long double toDouble();

	void abbr(); // 약분
};


