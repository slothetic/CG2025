#pragma once
#include <iostream>
#include <jsoncpp/json/json.h>
#include <fstream>
#include <iomanip>
#include <opencv2/opencv.hpp>
#include "MyNum.h"
#include <string>
#include <cmath>
#include <deque>
#include <set>
#include <random>
using namespace std;


class Point{
	public:
		MyNum x, y;
		Point();
		Point(int, int);
		Point(MyNum, MyNum);
		bool operator==(const Point&);
		bool operator!=(const Point&);
		friend std::ostream& operator<<(std::ostream&, const Point&);
};

long double angle(Point, Point, Point);
MyNum sqdist(Point, Point);

class Triangle{
	public:
		int p[3]; //CCW
		Triangle *t[3]; //neighbors, CCW, from p1p2. nullptr if the edge is boundary or constraint
		Triangle(int, int, int);
		~Triangle();
		int get_ind(int); //find index of vertex. return -1 if not exists
};

class Instance{
	public:
		string instance_name;
		int fp_ind; //fixed points
		std::vector<Point> pts;
		std::deque<int> boundary; //CCW
		std::set<std::pair<int,int>> constraints;
		std::set<Triangle*> triangles;
		Instance();
		Instance(int, std::vector<Point>, std::deque<int>, std::set<std::pair<int,int>>);
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
		void make_non_obtuse(Triangle*);
		void insert_point_on(std::pair<int, int>, Point);
		void step();

		void print_triangle(Triangle*);
		void DrawResult(string);
};

MyNum turn(Point, Point, Point); // if CCw, >0 / if CW, <0 / if colinear, ==0
Point projection(Point, Point, Point);
Point right_angle_point(Point, Point, Point, Point); //the point q on p3p4 that makes right angle p1p2q. If parallel, return Point(0, 0)
Point midpoint(Point, Point);
std::vector<Point> intersections_of_orthogonals(Point, Point, Point, Point); //the intersection points between the lines going through p1/p2 and orthogonal to p1p2, and the lines going through p3/p4 and orthogonal to p3p4
std::vector<Point> intersections_of_disks(Point, MyNum, Point, MyNum);
std::pair<int, int> sorted_pair(int, int);


// class Polygon{
// 	public:
// 		vector<cv::Point> vers;
// 		vector<int> x_vers;
// 		vector<int> y_vers;
// 		Polygon();
// 		Polygon(vector<cv::Point>);
// 		Polygon(vector<int>, vector<int>);
// 		bool intersect(Polygon);
// 		bool isin(Polygon);
// 		Polygon make_convex();
// 		int index;
// 		int value;
// 		int x_loc;
// 		int y_loc;
// 		bool use;
// 		bool cont;
// };

class Data{
	private:
	public:
		Data(){};
		~Data(){};

		string instance_name;
		string input;
		string type;
		string output;
		int num_points;
		int num_constraints;
		Instance *inst;

		void ReadData();
		void WriteData();
		void DrawResult();
};

