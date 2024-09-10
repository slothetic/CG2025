#pragma once

#include "MyInstance.h"
#include <string>


class Data{
	private:
	public:
		Data(){};
		~Data(){};

		std::string instance_name;
		std::string input;
		std::string type;
		std::string output;
		int num_points;
		int num_constraints;
		Instance *inst;

		void ReadData();
		void WriteData();
		void DrawResult();
};

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