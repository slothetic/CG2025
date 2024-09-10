#include "Point.h"

using namespace std;

Point::Point() {
}

Point::Point(int _x, int _y){ 
	x = MyNum(_x); 
	y = MyNum(_y);
}

Point::Point(MyNum _x, MyNum _y){ 
	x = _x; 
	y = _y; 
}

bool Point::operator==(const Point& _p) {
	return (this->x == _p.x) && (this->y == _p.y);
}

std::ostream& operator<<(std::ostream& out, const Point& _p) {
	out << "(" << _p.x << ", " << _p.y << ")";
	return out;
}

bool Point::operator!=(const Point& _p) {
	return (this->x != _p.x) || (this->y != _p.y);
}