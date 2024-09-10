#include "utility.h"

#include <assert.h>
#include <cmath>

long double angle(Point p1, Point p2, Point p3) {
	assert(p1 != p2);
	assert(p2 != p3);
	MyNum p12x = p2.x - p1.x;
	MyNum p12y = p2.y - p1.y;
	MyNum p23x = p2.x - p3.x;
	MyNum p23y = p2.y - p3.y;
	MyNum ab = p12x * p23x + p12y * p23y;
	MyNum a = p12x * p12x + p12y * p12y;
	MyNum b = p23x * p23x + p23y * p23y;
	if (turn(p1, p2, p3) == 0)
		return (ab >= MyNum(0)) ? -1. : 1.;
	else if (ab == MyNum(0))
		return 0.;
	long double dab = ab.toDouble();
	long double ra = std::sqrt(a.toDouble());
	long double rb = std::sqrt(b.toDouble());
	return -dab / ra / rb;
}

MyNum sqdist(Point p, Point q) {
	MyNum xd = p.x - q.x;
	MyNum yd = p.y - q.y;
	return xd * xd + yd * yd;
}

MyNum turn(Point p1, Point p2, Point p3) {
	return (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x);
}

std::pair<int, int> sorted_pair(int a, int b) {
	return (a > b) ? std::make_pair(b, a) : std::make_pair(a, b);
}