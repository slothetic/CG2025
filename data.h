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
using namespace std;


struct Point{
	MyNum x, y;
};

MyNum angle(Point, Point, Point);
MyNum sqdist(Point, Point);

struct Triangle{
		int p[3]; //CCW
		Triangle *t[3]; //neighbors, CCw, from p1p2
};

class Instance{
	public:
		int fp_ind; //fixed points
		std::vector<Point> pts;
		std::deque<int> boundary; //CCW
		std::vector<std::pair<int,int>> constraints;
		std::vector<Triangle> triangles;
		Instance();
		Instance(int, std::vector<Point> pts, std::deque<int>, std::vector<std::pair<int,int>>);
		bool is_obtuse(Triangle);
		bool is_on(std::pair<int, int>, Point);
		bool is_in(Triangle, Point);
		void triangulate();
		void triangulate_polygon(std::vector<int>);
		void ear_cut(Triangle*, int);
		void insert_point(Point);
		void insert_point(Point, Triangle*);
		Triangle* find_triangle(int, int); // find a triangle with edge. return nullptr if not exists
		void make_non_obtuse();
		void update_boundary();
		void update_constraints();
};

MyNum turn(Point, Point, Point); // if CCw, <0 / if CW, >0 / if colinear, ==0

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
		int x_max;
		int x_min;
		int y_max;
		int y_min;

		Polygon ReadData();
		//void WriteResult();
		//void DrawResult();
};

