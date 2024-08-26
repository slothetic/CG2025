#pragma once
#include<iostream>

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

