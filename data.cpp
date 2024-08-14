#include "data.h"

MyNum angle(Point p1, Point p2, Point p3){
	MyNum p12x = p2.x-p1.x;
	MyNum p12y = p2.y-p1.y;
	MyNum p23x = p2.x-p3.x;
	MyNum p23y = p2.y-p3.y;
	MyNum ab = p12x * p23x + p12y * p23y;
	MyNum a = p12x * p12x + p12y * p12y;
	MyNum b = p23x * p23x + p23y * p23y;
	return (ab.den >= 0) ? - ab * ab / a / b : ab * ab / a / b;
}

MyNum sqdist(Point p, Point q){
	MyNum xd = p.x - q.x;
	MyNum yd = p.y - q.y;
	return xd * xd + yd * yd;
}

Instance::Instance(){
	this->fp_ind = 0;
}

Instance::Instance(int _fp_ind, std::vector<Point> _pts, std::deque<int> _boundary, std::vector<std::pair<int, int>> _constraints){
	this->fp_ind = _fp_ind;
	this->pts = _pts;
	this->boundary = _boundary;
	this->constraints = _constraints;
}

bool Instance::is_obtuse(Triangle t){
	Point q1 = pts[t.p[0]];
	Point q2 = pts[t.p[1]];
	Point q3 = pts[t.p[2]];
	if (compute_angle(q1, q2, q3) > 0) return false;
	if (compute_angle(q2, q3, q1) > 0) return false;
	if (compute_angle(q3, q1, q2) > 0) return false;
	return true;
}

bool Instance::is_on(std::pair<int, int> e, Point p){
	Point q1 = pts[e.first];
	Point q2 = pts[e.second];
	if (turn(q1, q2, p) == MyNum(0)){
		if (q1.x == q2.x){
			MyNum y1 = (q1.y < q2.y) ? q1.y : q2.y;
			MyNum y2 = q1.y + q2.y - y1;
			return (q1.x == p.x) && (y1 < p.y) && (p.y < y2);
		}
		else {
			MyNum x1 = (q1.x < q2.x) ? q1.x : q2.x;
			MyNum x2 = q1.x + q2.x - x1;
			return (x1 < p.x) && (p.x < x2);
		}
	}
	else return false;
}

bool Instance::is_in(Triangle t, Point p){
	Point q1 = pts[t.p[0]];
	Point q2 = pts[t.p[1]];
	Point q3 = pts[t.p[2]];
	return (turn(q1, q2, p) <= MyNum(0)) && (angle(q1, q2, p) <= angle(q1, q2, q3)) && (angle(q2, q1, p) <= angle(q2, q1, q3));
}

void Instance::triangulate(){
	std::vector<bool> check(pts.size(), false);
	triangulate_polygon(this->boundary);
	for (int d : boundary)
		check[d] = true;
	for (int i; i < pts.size(); i++)
		if (!check[d])
			insert_point(pts[i]);
}

void Instance::triangulate_polygon(std::deque<int> polygon){
	if (polygon.size() == 3){
		Triangle t;
		t.p[0] = polygon[0];
		t.p[1] = polygon[1];
		t.p[2] = polygon[2];
		t.t[0] = nullptr;
		t.t[1] = nullptr;
		t.t[2] = nullptr;
		triangles.push_back(t);
	}
	else {
		while(turn(pts[polygon[polygon.size()-1]], pts[polygon[0]], pts[polygon[1]]) < MyNum(0))
			polygon.push_front(polygon.pop_back());
		Triangle t;
		t.p[0] = polygon[polygon.size()-1];
		t.p[1] = polygon[0];
		t.p[2] = polygon[1];
		t.t[0] = nullptr;
		t.t[1] = nullptr;
		t.t[2] = nullptr;
		int c = -1;
		Point q = pts[t.p[1]];
		MyNum d1 = sqdist(q, pts[t.p[0]]);
		MyNum d2 = sqdist(q, pts[t.p[2]]);
		MyNum cdist = (d1 > d2) ? d1 : d2;
		for (int i = 2; i < polygon.size()-1 ; i++) {
			if (is_in(t, pts[polygon[i]])) {
				MyNum d = sqdist(q, pts.[polygon[i]]);
				if (d < cdist){
					cdist = d;
					c = i;
				}
			}
		}
		if (c == -1){
			triangles.push_back(t);
			Triangle *tp = &triangles[triangles.size()-1];
			polygon.pop_front();
			triangulate_polygon(polygon);
			Triangle* tt = find_triangle(t.p[0], t.p[2]);
			tp->t[2] = tt;
			if (tt->p[0] == t.p[0])
				tt->t[0] = tp;
			else if (tt->p[1] == t.p[0])
				tt->t[1] = tp;
			else
				tt->t[2] = tp;
			balance_edge(tp, 2);
		}
		else {
			std::deque<int> poly1, poly2;
			poly1.insert(poly1.begin(), polygon.begin(), polygon.begin() + i + 1);
			poly2.insert(poly2.begin(), polygon.begin() + i, polygon.end());
			poly2.push_back(t.p[1]);
			triangulate_polygon(poly1);
			Triangle *t1 = find_triangle(t.p[1], polygon[c]);
			triangulate_polygon(poly2);
			Triangle *t2 = find_triangle(polygon[c], t.p[1]);
			if (t1->p[0] == t.p[1])
				t1->t[0] = t2;
			else if (t1->p[1] == t.p[1])
				t1->t[1] = t2;
			else
				t1->t[2] = t2;
			if (t2->p[1] == t.p[1])
				t2->t[0] = t1;
			else if (t2->p[2] == t.p[1])
				t2->t[1] = t1;
			else
				t2->t[2] = t1;
		}
	}
}

void Instance::balance_edge(Triangle* t, int n){
	Triangle tt = t->t[n];
	if (!tt)
		return;
	Point q1 = pts[t->p[(n + 1) % 3]];
	Point q2 = pts[t->p[(n + 2) % 3]];
	Point q3 = pts[t->p[n]];
	Point q4;
	int i;
	if (t->p[n] == tt->p[0]){
		q4 = pts[tt->p[1]];
	}
	else if (t->p[n] == tt->p[1]){
		q4 = pts[tt->p[2]];
	}
	else {
		q4 = pts[tt->p[0]];
	}
}

MyNum turn(Point p1, Point p2, Point p3){
	return (p2.x - p1.x) * (p3.y - p1.y)- (p2.y - p1.y) * (p3.x - p1.x);
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


