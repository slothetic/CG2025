#include "Triangle.h"

Triangle::Triangle(int a, int b, int c) {
	this->p[0] = a;
	this->p[1] = b;
	this->p[2] = c;
	this->t[0] = nullptr;
	this->t[1] = nullptr;
	this->t[2] = nullptr;
}

Triangle::~Triangle() {
}

int Triangle::get_ind(int q) {
	if (q == p[0])
		return 0;
	if (q == p[1])
		return 1;
	if (q == p[2])
		return 2;
	return -1;
}
