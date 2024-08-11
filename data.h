#pragma once
#include <iostream>
#include <jsoncpp/json/json.h>
#include <fstream>
#include <iomanip>
#include <opencv2/opencv.hpp>
#include "MyNum.h"
#include <string>
#include <cmath>
using namespace std;


class Point{
	public:
		MyNum x, y;
		Point();
		Point(int, int);
		Point(MyNum, MyNum);
};

float compute_angle(Point, Point, Point);

class Edge{
	public:
		Point s, t;
		Edge();
		Edge(Point, Point);
};

class Triangle{
	public:
		Point p1, p2, p3;
		Triangle(Point, Point, Point);
		bool is_obtuse();
};

class Polygon{
	public:
		std::vector<Point> vertex;
		int fv_ind; // fixed_vertex index
		std::vector<std::pair<int, int>> boundary; //CCW
		std::vector<std::pair<int, int>> constraint;
		std::vector<std::vector<std::pair<int, int>>>* edges; // Adjacency List, type(0: container, 1: constraint, 2: edge)
		Polygon(std::vector<Point>, std::vector<std::pair<int, int>>, std::vector<std::pair<int, int>>, std::vector<std::pair<int, int>> );
};
// bool is_left(cv::Point, cv::Point, cv::Point);

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

