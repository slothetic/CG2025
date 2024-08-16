#include "data.h"

Point::Point(){}

Point::Point(int _x, int _y){x = MyNum(_x); y = MyNum(_y);}

Point::Point(MyNum _x, MyNum _y){x = _x; y = _y;}

bool Point::operator==(const Point& _p) {
	return (this->x == _p.x) && (this->y == _p.y);
}


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

Triangle::Triangle(int a, int b, int c){
	this->p[0] = a;
	this->p[1] = b;
	this->p[2] = c;
}

Triangle::~Triangle(){
}

int Triangle::get_ind(int q){
	if (q==p[0])
		return 0;
	if (q==p[1])
		return 1;
	if (q==p[2])
		return 2;
	return -1;
}

Instance::Instance(){
	this->fp_ind = 0;
}

Instance::Instance(int _fp_ind, std::vector<Point> _pts, std::deque<int> _boundary, std::set<std::pair<int, int>> _constraints){
	this->fp_ind = _fp_ind;
	this->pts = _pts;
	this->boundary = _boundary;
	this->constraints = _constraints;
}

bool Instance::is_obtuse(Triangle *t){
	Point q1 = pts[t->p[0]];
	Point q2 = pts[t->p[1]];
	Point q3 = pts[t->p[2]];
	if (angle(q1, q2, q3) > 0) return false;
	if (angle(q2, q3, q1) > 0) return false;
	if (angle(q3, q1, q2) > 0) return false;
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

bool Instance::is_in(Triangle *t, Point p){
	Point q1 = pts[t->p[0]];
	Point q2 = pts[t->p[1]];
	Point q3 = pts[t->p[2]];
	return (turn(q1, q2, p) <= MyNum(0)) && (angle(q1, q2, p) <= angle(q1, q2, q3)) && (angle(q2, q1, p) <= angle(q2, q1, q3));
}

void Instance::triangulate(){
	std::vector<bool> check(pts.size(), false);
	triangulate_polygon(this->boundary);
	for (int d : boundary)
		check[d] = true;
	for (int i; i < pts.size(); i++)
		if (!check[i])
			insert_point(i);
	for (std::pair<int, int> con : constraints)
		resolve_cross(con);
}

void Instance::triangulate_polygon(std::deque<int> polygon){
	if (polygon.size() == 3){
		Triangle *t = new Triangle(polygon[0], polygon[1], polygon[2]);
		t->t[0] = nullptr;
		t->t[1] = nullptr;
		t->t[2] = nullptr;
		triangles.insert(t);
	}
	else {
		while(turn(pts[polygon[polygon.size() - 1]], pts[polygon[0]], pts[polygon[1]]) < MyNum(0)){
			polygon.push_front(polygon[polygon.size() - 1]);
			polygon.pop_back();
		}
		Triangle *t = new Triangle(polygon[polygon.size() - 1], polygon[0], polygon[1]);
		t->t[0] = nullptr;
		t->t[1] = nullptr;
		t->t[2] = nullptr;
		int c = -1;
		Point q = pts[polygon[0]];
		MyNum d1 = sqdist(q, pts[t->p[0]]);
		MyNum d2 = sqdist(q, pts[t->p[2]]);
		MyNum cdist = (d1 > d2) ? d1 : d2;
		for (int i = 2; i < polygon.size() - 1 ; i++) {
			if (is_in(t, pts[polygon[i]])) {
				MyNum d = sqdist(q, pts[polygon[i]]);
				if (d < cdist){
					cdist = d;
					c = i;
				}
			}
		}
		if (c == -1){
			triangles.insert(t);
			polygon.pop_front();
			triangulate_polygon(polygon);
			Triangle* tt = find_triangle(t->p[0], t->p[2]);
			t->t[2] = tt;
			if (tt->p[0] == t->p[0])
				tt->t[0] = t;
			else if (tt->p[1] == t->p[0])
				tt->t[1] = t;
			else
				tt->t[2] = t;
		}
		else {
			std::deque<int> poly1, poly2;
			poly1.insert(poly1.begin(), polygon.begin(), polygon.begin() + c + 1);
			poly2.insert(poly2.begin(), polygon.begin() + c, polygon.end());
			poly2.push_back(t->p[1]);
			triangulate_polygon(poly1);
			Triangle *t1 = find_triangle(polygon[c], t->p[1]);
			triangulate_polygon(poly2);
			Triangle *t2 = find_triangle(t->p[1], polygon[c]);
			if (t1->p[0] == t->p[1])
				t1->t[0] = t2;
			else if (t1->p[1] == t->p[1])
				t1->t[1] = t2;
			else
				t1->t[2] = t2;
			if (t2->p[1] == t->p[1])
				t2->t[0] = t1;
			else if (t2->p[2] == t->p[1])
				t2->t[1] = t1;
			else
				t2->t[2] = t1;
		}
	}
}

void Instance::insert_point(int p_ind) {
	Point q = pts[p_ind];
	for (Triangle* t : triangles) {
		if (is_in(t, q)){ 
			Triangle *t1, *t2;
			Triangle *tt = nullptr;
			int i, j;
			if (is_on(std::make_pair(t->p[0], t->p[1]), q)) {
				i = 0;
				tt = t->t[0];
			}
			else if (is_on(std::make_pair(t->p[1], t->p[2]), q)) {
				i = 1;
				tt = t->t[1];
			}
			else if (is_on(std::make_pair(t->p[2], t->p[0]), q)) {
				i = 2;
				tt = t->t[2];
			}
			if (tt) {
				if (t == tt->t[0])
					j = 0;
				else if (t == tt->t[1])
					j = 1;
				else
					j = 2;
				t1 = new Triangle(p_ind, t->p[(i + 1) % 3], t->p[(i + 2) % 3]);
				t1->t[0] = tt;
				t1->t[1] = t->t[(i + 1) % 3];
				t1->t[2] = t;
				t2 = new Triangle(p_ind, tt->p[(j + 1) % 3], tt->p[(j + 2) % 3]);
				t2->t[0] = t;
				t2->t[1] = tt->t[(j + 1) % 3];
				t2->t[2] = tt;
				t->p[(i + 1) % 3] = p_ind;
				t->t[i] = t2;
				t->t[(i + 1) % 3] = t1;
				tt->p[(j + 1) % 3] = p_ind;
				tt->t[j] = t1;
				tt->t[(i + 1) % 3] = t2;
			}
			else {
				t1 = new Triangle(p_ind, t->p[1], t->p[2]);
				t1->t[1] = t->t[1];
				t2 = new Triangle(p_ind, t->p[2], t->p[0]);
				t2->t[1] = t->t[2];
				t->p[2] = p_ind;
				t->t[1] = t1;
				t->t[2] = t2;
				t1->t[0] = t;
				t1->t[2] = t2;
				t2->t[0] = t1;
				t2->t[2] = t;
			}
			triangles.insert(t1);
			triangles.insert(t2);
			break;
		}
	}
}

void Instance::resolve_cross(std::pair<int, int> con) {
	int q1 = con.first;
	int q2 = con.second;
	for (Triangle *t : triangles) {
		int i = t->get_ind(q1);
		if (i != -1) {
			Point r1 = pts[q1];
			Point r2 = pts[t->p[(i + 1) % 3]];
			Point r3 = pts[t->p[(i + 2) % 3]];
			Point r4 = pts[q2];
			MyNum ang = angle(r2, r1, r3);
			while (angle(r2, r1, r4) <= ang && angle(r3, r1, r4) <= ang){
				t = t->t[i];
				i = t->get_ind(q1);
				r2 = pts[t->p[(i + 1) % 3]];
				r3 = pts[t->p[(i + 2) % 3]];
				ang = angle(r2, r1, r3);
			}
			if (r2 == r4) {
				Triangle *tt = t->t[i];
				t->t[i] = nullptr;
				int j = tt->get_ind(q2);
				tt->t[j] = nullptr;
			}
			else if (r3 == r4) {
				Triangle *tt = t->t[(i + 2) % 3];
				t->t[(i + 2) % 3] = nullptr;
				int j = tt->get_ind(q1);
				tt->t[j] = nullptr;
			}
			else
				resolve_cross(con, t);
			return;
		}
	}
}

void Instance::resolve_cross(std::pair<int, int> con, Triangle* t) {
	int q1 = con.first;
	int q2 = con.second;
	int i = t->get_ind(q1);
	Triangle *tt = t->t[(i + 1) % 3];
	int j = (tt->get_ind(t->p[(i + 1) % 3]) + 1) % 3;
	int r = tt->p[j];
	Triangle *ti = t->t[(i + 2) % 3];
	Triangle *tj = tt->t[(j + 2) % 3];
	t->p[(i + 2) % 3] = r;
	t->t[(i + 1) % 3] = tj;
	tt->p[(j + 2) % 3] = q1;
	tt->t[(j + 1) % 3] = ti;
	if (r==q2) {
		t->t[(i + 2) % 3] = nullptr;
		tt->t[(j + 2) % 3] = nullptr;
	}
	else {
		t->t[(i + 2) % 3] = tt;
		tt->t[(j + 2) % 3] = t;
		if (angle(pts[q2], pts[q1], pts[t->p[(i + 1) % 3]]) < angle(pts[r], pts[q1], pts[t->p[(i + 1) % 3]]))
			resolve_cross(con, t);
		else
			resolve_cross(con, tt);
	}
}

//TODO


Triangle* Instance::find_triangle(int q1, int q2){
	for (Triangle* t : triangles) {
		if (t->p[0] == q1 && t->p[1] == q2)
			return t;
		if (t->p[1] == q1 && t->p[2] == q2)
			return t;
		if (t->p[2] == q1 && t->p[0] == q2)
			return t;
	}
	return nullptr;
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


void Data::ReadData(){
	cout << "--------------------ReadData--------------------" << endl;
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
	std::deque<int> region_boundary;
	for (int i=0;i<_region_boundary.size();i++){
		region_boundary.push_back(_region_boundary[i].asInt());
	}
	Json::Value _num_constraints = root["num_constraints"];
	num_constraints = _num_constraints.asInt();
	Json::Value _constraints = root["additional_constraints"];
	std::set<std::pair<int,int>> constraints;
	for (int i=0; i<_num_constraints.size(); i++){
		constraints.insert(std::make_pair(_constraints[i][0].asInt(), _constraints[i][1].asInt()));
	}
	inst = new Instance(num_points, pts, region_boundary, constraints);
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
	for (std::pair<int, int> e : inst->constraints)
		const_edges.insert(e);
	for (int i = 1 ; i < inst->boundary.size() ; i++)
		const_edges.insert(std::make_pair(inst->boundary[i-1], inst->boundary[i]));
	const_edges.insert(std::make_pair(inst->boundary[0], inst->boundary[inst->boundary.size()-1]));
	for (Triangle* t : inst->triangles) {
		std::pair<int, int> e1 = std::make_pair(t->p[0], t->p[1]);
		std::pair<int, int> e2 = std::make_pair(t->p[1], t->p[2]);
		auto cend = const_edges.end();
		auto iend = int_edges.end();
		if (const_edges.find(e1) == cend && const_edges.find(e2) == cend && int_edges.find(e1) == iend && int_edges.find(e2) == iend)
			int_edges.insert(e1);
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


