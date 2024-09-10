#pragma once

#include <string>
#include <vector>
#include <set>
#include <deque>
#include <utility>

#include "Point.h"
#include "Triangle.h"

class Instance {
public:
	std::string instance_name;
	int fp_ind; //fixed points
	std::vector<Point> pts;
	std::deque<int> boundary; //CCW
	std::set<std::pair<int, int>> constraints;
	std::set<Triangle*> triangles;
	Instance();
	Instance(int, std::vector<Point>, std::deque<int>, std::set<std::pair<int, int>>);
	bool is_obtuse(Triangle*);
	bool is_on(std::pair<int, int>, Point);
	bool is_in(Triangle*, Point);
	void triangulate();
	void triangulate_polygon(std::deque<int>);
	void insert_point(int);
	void resolve_cross(std::pair<int, int>);
	void resolve_cross(std::pair<int, int>, Triangle*);
	void flip(Triangle*, int);
	void minmax_triangulate();
	bool ear_cut(Triangle*, int);
	Triangle* find_triangle(int, int); // find a triangle with edge. return nullptr if not exists
	void make_non_obtuse();
	void update_boundary();
	void update_constraints();
	void print_triangle(Triangle*);
	void add_steiner(Point);
	void delete_steiner(Point);
	void DrawResult(std::string);
};