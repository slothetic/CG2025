#pragma once

#include <utility>

#include "Point.h"
#include "MyNum.h"


long double angle(Point, Point, Point);

MyNum sqdist(Point, Point);

MyNum turn(Point p1, Point p2, Point p3); // if CCw, >0 / if CW, <0 / if colinear, == 0

std::pair<int, int> sorted_pair(int, int);