#pragma once
#include<iostream>
#include<vector>

class BigNum{
	public:
		std::vector<unsigned long long int> nums;
		bool sgn;

		BigNum();
		BigNum(long long int);

		BigNum operator-();
		BigNum& operator=(const BigNum&);
		BigNum operator+(const BigNum&);
		BigNum operator-(const BigNum&);
		BigNum operator*(const BigNum&);
		BigNum operator==(const BigNum&);
		BigNum operator!=(const BigNum&);
		BigNum operator<(const BigNum&);
		BigNum operator>(const BigNum&);
		BigNum operator<=(const BigNum&);
		BigNum operator>=(const BigNum&);
		friend std::ostream& operator<<(std::ostream&, const BigNum&);
}

BigNum abs(const BigNum&);

class MyNum{
	public:
		long long int den, num;

		MyNum();
		MyNum(long long int);
		MyNum(long long int, long long int);

		MyNum operator-();
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
		
		void abbr();
};

long double to_Double(MyNum);

