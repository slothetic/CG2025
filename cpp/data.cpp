#include "data.h"
//#include <jsoncpp/json/json.h>
#include "include/json/json.h"
#include <opencv2/opencv.hpp>
//#include <cassert>
//#include <tuple>
#include <vector>

#include "utility.h"

#include <string>
#include <fstream>
#include <random>


#pragma comment(lib, "jsoncpp.lib")

using namespace std;

void Data::ReadData(){
	cout << "--------------------ReadData--------------------" << endl;
	Json::Value root;
	Json::Reader reader;
	string path=input;
	ifstream json(path, ifstream::binary);
	reader.parse(json, root);

	instance_name =  root["instance_uid"].asString();
	num_points = root["num_points"].asInt();
	const Json::Value _points_x = root["points_x"];
	const Json::Value _points_y = root["points_y"];
	vector<Point> pts;
	for (int i = 0; i < _points_x.size(); i++){
		pts.emplace_back(_points_x[i].asInt(), _points_y[i].asInt());
	}
	Json::Value _region_boundary = root["region_boundary"];
	std::deque<int> region_boundary;
	for (int i = 0; i < _region_boundary.size(); i++) {
		region_boundary.push_back(_region_boundary[i].asInt());
	}
	Json::Value _num_constraints = root["num_constraints"];
	num_constraints = _num_constraints.asInt();
	Json::Value _constraints = root["additional_constraints"];
	std::set<std::pair<int,int>> constraints;
	for (int i=0; i<_constraints.size(); i++){
		constraints.insert(std::make_pair(_constraints[i][0].asInt(), _constraints[i][1].asInt()));
	}
	inst = new Instance(num_points, pts, region_boundary, constraints);
	inst->instance_name = instance_name;
}

void Data::WriteData(){
	ofstream fout;
	fout.open("solutions/" + instance_name + ".solution.json");
	fout << "{" << endl;
	fout << "  \"content_type\": \"CG_SHOP_2025_Solution\"," << endl;
	fout << "  \"instance_uid\": \"" << instance_name << "\"," << endl;
	fout << "  \"steiner_point_x\": [";
	for (int i = inst->fp_ind; i < inst->pts.size() ; i++){
		fout << inst->pts[i].x;
		if (i < inst->pts.size() - 1)
			fout << ", ";
	}
	fout << "]," << endl;
	fout << "  \"steiner_point_y\": [";
	for (int i = inst->fp_ind; i < inst->pts.size() ; i++){
		fout << inst->pts[i].y;
		if (i < inst->pts.size() - 1)
			fout << ", ";
	}
	fout << "]," << endl;
	std::set<std::pair<int, int>> const_edges;
	std::set<std::pair<int, int>> int_edges;
	for (std::pair<int, int> e : inst->constraints){
		const_edges.insert(sorted_pair(e.first, e.second));
	}
	for (int i = 1 ; i < inst->boundary.size() ; i++)
		const_edges.insert(sorted_pair(inst->boundary[i-1], inst->boundary[i]));
	const_edges.insert(sorted_pair(inst->boundary[0], inst->boundary[inst->boundary.size()-1]));
	cout<<"Number of Triangles: "<< inst->triangles.size() <<endl;
	for (Triangle* t : inst->triangles) {
		std::pair<int, int> e1 = sorted_pair(t->p[0], t->p[1]);
		std::pair<int, int> e2 = sorted_pair(t->p[1], t->p[2]);
		std::pair<int, int> e3 = sorted_pair(t->p[0], t->p[2]);
		auto cend = const_edges.end();
		auto iend = int_edges.end();
		// if (const_edges.find(e1) == cend && const_edges.find(e2) == cend && int_edges.find(e1) == iend && int_edges.find(e2) == iend)
		// 	int_edges.insert(e1);
		if (const_edges.find(e1) == cend && int_edges.find(e1) == iend)
			int_edges.insert(e1);
		if (const_edges.find(e2) == cend && int_edges.find(e2) == iend)
			int_edges.insert(e2);
		if (const_edges.find(e3) == cend && int_edges.find(e3) == iend)
			int_edges.insert(e3);
	}
	fout << "  \"edges\": [" << endl;
	int cnt = 1;
	for (std::pair<int, int> e : int_edges){
		fout << "    [" << e.first << ", " << e.second << "]";
		if (cnt < int_edges.size()) {
			fout << ",";
			cnt ++;
		}
		fout << endl;
	}
	fout << "  ]" << endl << "}" << endl;
	fout.close();
}

void Data::DrawResult(){
	MyNum minx(inst->pts[0].x);
	MyNum miny(inst->pts[0].y);
	MyNum maxx(inst->pts[0].x);
	MyNum maxy(inst->pts[0].y);
	for (int i = 0; i < inst->pts.size() ; i++){
		if (minx>MyNum(inst->pts[i].x)) minx=MyNum(inst->pts[i].x);
		if (miny>MyNum(inst->pts[i].y)) miny=MyNum(inst->pts[i].y);
		if (maxx<MyNum(inst->pts[i].x)) maxx=MyNum(inst->pts[i].x);
		if (maxy<MyNum(inst->pts[i].y)) maxy=MyNum(inst->pts[i].y);
	}
	long long int width = (long long int)(maxx-minx).toDouble();
	long long int height = (long long int)(maxy-miny).toDouble();
	float rad = 1000./width;
	width = (int)width*rad+40;
	height = (int)height*rad+40;
	int minw = 20-(int)minx.toDouble()*rad;
	int minh = height+(int)miny.toDouble()*rad-20;
	//cout<<"miny: "<<miny<<" maxy:" <<maxy<< " minh: "<<minh<<endl;


	cv::Mat img(height, width, CV_8UC3, cv::Scalar(255,255,255));
	std::random_device rd;
	std::mt19937 gen(rd());
	std::uniform_int_distribution<int> dis(220, 255);
	for (Triangle* t : inst->triangles) {
		cv::Point triangle_pt[1][3]; 
		triangle_pt[0][0] = cv::Point(minw+(int)inst->pts[t->p[0]].x.toDouble()*rad, minh-(int)inst->pts[t->p[0]].y.toDouble()*rad); 
		triangle_pt[0][1] = cv::Point(minw+(int)inst->pts[t->p[1]].x.toDouble()*rad, minh-(int)inst->pts[t->p[1]].y.toDouble()*rad); 
		triangle_pt[0][2] = cv::Point(minw+(int)inst->pts[t->p[2]].x.toDouble()*rad, minh-(int)inst->pts[t->p[2]].y.toDouble()*rad); 
		const cv::Point* ppt[1] = { triangle_pt[0] };
		int npt[] = { 3 };
		
		fillPoly(img, ppt, npt, 1, cv::Scalar(dis(gen), dis(gen), dis(gen)), 8);
	}

	std::set<std::pair<int, int>> const_edges;
	std::set<std::pair<int, int>> int_edges;
	for (std::pair<int, int> e : inst->constraints){
		const_edges.insert(sorted_pair(e.first, e.second));
		cv::line(img, cv::Point(minw+(int)inst->pts[e.first].x.toDouble()*rad,minh-(int)inst->pts[e.first].y.toDouble()*rad), cv::Point(minw+(int)inst->pts[e.second].x.toDouble()*rad,minh-(int)inst->pts[e.second].y.toDouble()*rad), cv::Scalar(0,0,255), 2);
	}
	cout<<inst->boundary.size()<<endl;
	for (int i = 1 ; i < inst->boundary.size() ; i++){
		const_edges.insert(sorted_pair(inst->boundary[i-1], inst->boundary[i]));
		cv::line(img, cv::Point(minw+(int)inst->pts[inst->boundary[i-1]].x.toDouble()*rad,minh-(int)inst->pts[inst->boundary[i-1]].y.toDouble()*rad), cv::Point(minw+(int)inst->pts[inst->boundary[i]].x.toDouble()*rad,minh-(int)inst->pts[inst->boundary[i]].y.toDouble()*rad), cv::Scalar(255,0,0), 2);
	}
	const_edges.insert(sorted_pair(inst->boundary[0], inst->boundary[inst->boundary.size()-1]));
	//cout<<"const edges"<<endl;
	//for (std::pair<int, int> e:const_edges)
		//cout<<e.first<<" "<<e.second<<endl;
	cv::line(img, cv::Point(minw+(int)inst->pts[inst->boundary[0]].x.toDouble()*rad,minh-(int)inst->pts[inst->boundary[0]].y.toDouble()*rad), cv::Point(minw+(int)inst->pts[inst->boundary[inst->boundary.size()-1]].x.toDouble()*rad,minh-(int)inst->pts[inst->boundary[inst->boundary.size()-1]].y.toDouble()*rad), cv::Scalar(255,0,0), 2);
	//cout<<"new edges"<<endl;
	for (Triangle* t : inst->triangles) {
		std::pair<int, int> e1 = sorted_pair(t->p[0], t->p[1]);
		std::pair<int, int> e2 = sorted_pair(t->p[1], t->p[2]);
		std::pair<int, int> e3 = sorted_pair(t->p[0], t->p[2]);
		auto cend = const_edges.end();
		auto iend = int_edges.end();
		if (const_edges.find(e1) == cend && int_edges.find(e1) == iend){
			int_edges.insert(e1);
			cv::line(img, cv::Point(minw+(int)inst->pts[e1.first].x.toDouble()*rad,minh-(int)inst->pts[e1.first].y.toDouble()*rad), cv::Point(minw+(int)inst->pts[e1.second].x.toDouble()*rad,minh-(int)inst->pts[e1.second].y.toDouble()*rad), cv::Scalar(0,0,0), 2);
		}
		if (const_edges.find(e2) == cend && int_edges.find(e2) == iend){
			int_edges.insert(e2);
			cv::line(img, cv::Point(minw+(int)inst->pts[e2.first].x.toDouble()*rad,minh-(int)inst->pts[e2.first].y.toDouble()*rad), cv::Point(minw+(int)inst->pts[e2.second].x.toDouble()*rad,minh-(int)inst->pts[e2.second].y.toDouble()*rad), cv::Scalar(0,0,0), 2);
		}
		if (const_edges.find(e3) == cend && int_edges.find(e3) == iend){
			int_edges.insert(e3);
			cv::line(img, cv::Point(minw+(int)inst->pts[e3.first].x.toDouble()*rad,minh-(int)inst->pts[e3.first].y.toDouble()*rad), cv::Point(minw+(int)inst->pts[e3.second].x.toDouble()*rad,minh-(int)inst->pts[e3.second].y.toDouble()*rad), cv::Scalar(0,0,0), 2);
		}
	}
	for (int i = 0; i < inst->pts.size() ; i++){
		if (i<inst->fp_ind) cv::circle(img, cv::Point(minw+(int)inst->pts[i].x.toDouble()*rad,minh-(int)inst->pts[i].y.toDouble()*rad),5,cv::Scalar(0,0,0),cv::FILLED);
		else cv::circle(img, cv::Point(minw+(int)inst->pts[i].x.toDouble()*rad,minh-(int)inst->pts[i].y.toDouble()*rad),5,cv::Scalar(255,0,0),cv::FILLED);
	}

	cv::imwrite("solutions/" + instance_name + ".solution.png", img);
}

// Polygon::Polygon(){vers.assign(1, cv::Point());x_loc=0;y_loc=0;}

// Polygon::Polygon(vector<cv::Point> _vers){
// 	vers = _vers;
// 	x_loc=0;
// 	y_loc=0;
// 	for (int i=0;i<vers.size();i++){
// 		x_vers.push_back(vers[i].x);
// 		y_vers.push_back(vers[i].y);
// 	}
// 	use=false;
// }

// Polygon::Polygon(vector<int> _x_vers, vector<int> _y_vers){
// 	x_vers = _x_vers;
// 	y_vers = _y_vers;
// 	x_loc=0;
// 	y_loc=0;
// 	for (int i=0;i<x_vers.size();i++){
// 		vers.push_back(cv::Point(x_vers[i], y_vers[i]));
// 	}
// 	use=false;
// }

// Polygon Polygon::make_convex(){
// 	vector<cv::Point> vers;
// 	int max_x = 0;
// 	int max_x_ind = 0;
// 	for (int i=0;i<this->vers.size();i++){
// 		if (this->x_vers[i]>max_x){
// 			max_x = this->x_vers[i];
// 			max_x_ind = i;
// 		}
// 	}
// 	vers.push_back(this->vers[max_x_ind]);
// 	for (int i=0;i<this->vers.size();i++){
// 		int ind = (i+max_x_ind+1)%(this->vers.size());
// 		if (vers.size()==1){
// 			vers.push_back(this->vers[ind]);
// 		}
// 		else{
// 			while(is_left(vers[-2], vers[-1], this->vers[ind])) {
// 				vers.pop_back();
// 				if (vers.size()==1) break;
// 			}
// 			vers.push_back(this->vers[ind]);
// 		}
// 	}
// 	vers.pop_back();
// 	Polygon newP = Polygon(vers);
// 	return newP;
// }

// bool Polygon::intersect(Polygon P){
// 	return true;	
// }

