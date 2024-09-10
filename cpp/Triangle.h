#pragma once

class Triangle {
public:
	int p[3]; //CCW
	Triangle* t[3]; //neighbors, CCW, from p1p2. nullptr if the edge is boundary or constraint
	Triangle(int, int, int);
	~Triangle();
	int get_ind(int); //find index of vertex. return -1 if not exists
};
