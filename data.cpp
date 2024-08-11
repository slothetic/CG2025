#include "data.h"

Point::Point(){x=MyNum(0);y=MyNum(0);}
Point::Point(int _x, int _y){x=MyNum(_x); y=MyNum(_y);}
Point::Point(MyNum _x, MyNum _y){x=_x, y=_y;}

float compute_angle(Point p1, Point p2, Point p3){
	MyNum p12x = p2.x-p1.x;
	MyNum p12y = p2.y-p1.y;
	MyNum p23x = p2.x-p3.x;
	MyNum p23y = p2.y-p3.y;
	return (p12x*p23x+p12y*p23y).toDouble()/(sqrt(pow(p12x.toDouble(),2)+pow(p12y.toDouble(),2))*sqrt(pow(p23x.toDouble(),2)+pow(p23y.toDouble(),2)));
}

Edge::Edge(){s=Point();t=Point();}
Edge::Edge(Point _s, Point _t){s=_s,t=_t;}

Triangle::Triangle(Point _p1, Point _p2, Point _p3){p1=_p1, p2=_p2, p3=_p3;} // CounterClockwise Order
bool Triangle::is_obtuse(){
	if (compute_angle(this->p1, this->p2, this->p3)<-EPS) {
		//std::cout<< compute_angle(this->p1, this->p2, this->p3)<< std::endl;
		return true;
	}
	if (compute_angle(this->p2, this->p3, this->p1)<-EPS) {
		//std::cout<< compute_angle(this->p2, this->p3, this->p1)<< std::endl;
		return true;
	}
	if (compute_angle(this->p3, this->p1, this->p2)<-EPS) {
		//std::cout<< compute_angle(this->p3, this->p1, this->p2)<< std::endl;
		return true;
	}
	return false;
}

Polygon::Polygon(std::vector<Point> _vertex, std::vector<std::pair<int, int>> _container, std::vector<std::pair<int, int>> _constraint, std::vector<std::pair<int, int>> _edges ){
	vertex = _vertex;
	boundary = _container;
	constraint = _constraint;
	// edges = new vector<>(n, 100)
	//vector<int> edges(n,10);

}

// bool is_left(cv::Point p1, cv::Point p2, cv::Point p3){
// 	return (p2.x-p1.x)*(p3.y-p1.y)-(p2.y-p1.y)*(p3.x-p1.x)>0;
// }

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

Polygon Data::ReadData(){
	cout << "--------------------ReadData--------------------" << endl;
	x_max= 0;
	y_max =0;
	Json::Value root;
	Json::Reader reader;
	string path=input;
	ifstream json(path, ifstream::binary);
	reader.parse(json, root);

	instance_name =  root["instance_uid"].asString();
	num_points = root["num_points"].asInt();
	Json::Value _points_x = root["points_x"];
	Json::Value _points_y = root["points_y"];
	vector<Point> pts;
	for (int i=0;i<_points_x.size();i++){
		pts.push_back(Point(_points_x[i].asInt(), _points_y[i].asInt()));
	}
	Json::Value _region_boundary = root["region_boundary"];
	std::vector<std::pair<int, int>> region_boundary;
	for (int i=1;i<_region_boundary.size();i++){
		region_boundary.push_back(std::make_pair(_region_boundary[i-1].asInt(), _region_boundary[i].asInt()));
	}
	region_boundary.push_back(std::make_pair(_region_boundary[_region_boundary.size()-1].asInt(), _region_boundary[0].asInt()));
	Json::Value _num_constraints = root["num_constraints"];
	std::vector<std::pair<int, int>> num_constraints;
	for (int i=1;i<_num_constraints.size();i++){
		num_constraints.push_back(std::make_pair(_num_constraints[i-1].asInt(), _num_constraints[i].asInt()));
	}
	Polygon res(pts, region_boundary, num_constraints, {});
	return res;
}


	// container = Polygon(c_vers);
	// container.cont = true;
	// int ind = 0;
	// for (auto& item:root["items"]){
	// 	int _value = item["vlaue"].asInt();
	// 	vector<cv::Point> i_vers;

	//   for (int i=0;i<_container["x"].size();i++){
	// 	  c_vers.push_back(cv::Point(_container["x"][i].asInt(), _container["y"][i].asInt()));
	//   }
	// 	Polygon P = Polygon(c_vers);
	// 	P.value = _value;
	// 	P.index = ind;
	// 	ind++;
	// 	for (int j=0;j<item["quantity"].asInt();j++){
	// 		items.push_back(P);
	// 	}
		
	// }

	// type = root["type"].asString();
	// cout << "-number of items: " << items.size() << endl;

// void Feasible::WriteResult(){
// 	cout << "--------------------WriteResult--------------------" << endl;

// 	int num_item=0;
// 	int value_item=0;
// 	vector<int> item_indices;
// 	vector<int> x_trans;
// 	vector<int> y_trans;
// 	for (auto& item:items){
// 		if (item.use) {
// 			num_item++;
// 			value_item=value_item+item.value;
// 			item_indices.push_back(item.index);
// 			x_trans.push_back(item.x_loc);
// 			y_trans.push_back(item.y_loc);
// 		}
// 	}
// 	string filename;
// 	filename = instance_name+"_result.json";
// 	ofstream solution(filename);

// 	solution<<"{\"type\": \"cgshop2024_solution\",\n";
// 	solution<<"\"instance_name\": \""<< instance_name <<"\",\n";
// 	solution<<"\"num_included_items\": \""<< num_item <<"\",\n";
// 	/*
// 	solution<<"\"total_value\": \""<< value_item <<"\",\n";
// 	solution<<"\"container\": {\"x\": [";
// 	for (int i=0;i<container.vers.size();i++){
// 		if (i<container.vers.size()-1){
// 			solution<<container.x_vers[i]<<", ";
// 		}
// 		else{
// 			solution<<container.x_vers[i]<<"],\n";
// 		}
// 	}
// 	solution<<"\"y\": [";
// 	for (int i=0;i<container.vers.size();i++){
// 		if (i<container.vers.size()-1){
// 			solution<<container.y_vers[i]<<", ";
// 		}
// 		else{
// 			solution<<container.y_vers[i]<<"]},\n";
// 		}

// 	}
// 	solution<<"\"items\": [";
// 	solution<<"]\n";
// 	*/

// 	solution<<"\"item_indices\": "<< "[";
// 	for (int i=0;i<item_indices.size();i++){
// 		if (i<item_indices.size()-1){
// 			solution<<item_indices[i]<<", ";
// 		}
// 		else{
// 			solution<<item_indices[i];
// 		}
// 	}
// 	solution<<"],\n";

// 	solution<<"\"x_trans\": "<< "[";
// 	for (int i=0;i<x_trans.size();i++){
// 		if (i<x_trans.size()-1){
// 			solution<<x_trans[i]<<", ";
// 		}
// 		else{
// 			solution<<x_trans[i];
// 		}
// 	}
// 	solution<<"],\n";
// 	solution<<"\"y_trans\": "<< "[";
// 	for (int i=0;i<y_trans.size();i++){
// 		if (i<y_trans.size()-1){
// 			solution<<y_trans[i]<<", ";
// 		}
// 		else{
// 			solution<<y_trans[i];
// 		}
// 	}
// 	solution<<"],\n";
//   solution<<"}\n";
// 	solution.close();
// }


// void Feasible::DrawResult(){
// 	cout << "--------------------DrawResult--------------------" << endl;
// 	float xy_max = min(x_max, y_max);
// 	float ratio = 400./xy_max;
// 	cv::Mat img(int(ratio*x_max*1.08), int(ratio*y_max*1.08), CV_8UC3, cv::Scalar(255, 255, 255));
// 	vector<cv::Point> vers;
// 	for (auto p:container.vers){
// 		vers.push_back(cv::Point(int(p.x*ratio), int(p.y*ratio)));
// 	}
// 	cv::polylines(img, vers, true, cv::Scalar(255, 0, 255), 2);

// 	cv::imwrite("check.bmp", img, vector<int>());
// }


