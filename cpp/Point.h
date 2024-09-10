#pragma once

#include <iostream>

#include "MyNum.h"


class Point {
public:
	MyNum x, y;
	Point();
	Point(int, int);
	Point(MyNum, MyNum);
	bool operator==(const Point&);
	bool operator!=(const Point&);
	friend std::ostream& operator<<(std::ostream&, const Point&);
};
