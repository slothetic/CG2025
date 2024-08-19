#include "data.h"

Point::Point(){}

Point::Point(int _x, int _y){x = MyNum(_x); y = MyNum(_y);}

Point::Point(MyNum _x, MyNum _y){x = _x; y = _y;}

bool Point::operator==(const Point& _p) {
	return (this->x == _p.x) && (this->y == _p.y);
}

std::ostream& operator<<(std::ostream& out, const Point& _p){
	out << "(" << _p.x << ", " << _p.y << ")";
	return out;
}

bool Point::operator!=(const Point&_p) {
	return (this->x != _p.x) || (this->y != _p.y);
}


MyNum angle(Point p1, Point p2, Point p3){
	assert(p1 != p2);
	assert(p2 != p3);
	// std::cout << p1 << std::endl;
	// std::cout << p2 << std::endl;
	// std::cout << p3 << std::endl;
	MyNum p12x = p2.x-p1.x;
	MyNum p12y = p2.y-p1.y;
	MyNum p23x = p2.x-p3.x;
	MyNum p23y = p2.y-p3.y;
	// std::cout << p12x << std::endl;
	// std::cout << p12y << std::endl;
	// std::cout << p23x << std::endl;
	// std::cout << p23y << std::endl;
	MyNum ab = p12x * p23x + p12y * p23y;
	MyNum a = p12x * p12x + p12y * p12y;
	MyNum b = p23x * p23x + p23y * p23y;
	// std::cout << ab << std::endl;
	// std::cout << a << std::endl;
	// std::cout << b << std::endl;
	// std::cout << ab * ab << std::endl;
	// std::cout << a * b << std::endl;
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
	MyNum zero(0);
	return (turn(q1, q2, p) >= zero) && (turn(q2, q3, p) >= zero) && (turn(q3, q1, p) >= zero);
}

void Instance::triangulate(){
	std::vector<bool> check(pts.size(), false);
	triangulate_polygon(this->boundary);
	//std::cout << boundary.size() << " " << triangles.size() << std::endl;
	for (int d : boundary)
		check[d] = true;
	for (int i; i < pts.size(); i++)
		if (!check[i]){
			insert_point(i);
			//std::cout << "inserted " << i << ": " << triangles.size() << std::endl;
		}
	int i=0;
	DrawResult(std::to_string(i));
	for (std::pair<int, int> con : constraints){
		i++;
		resolve_cross(con);
		DrawResult(std::to_string(i));
	}
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
			polygon.push_back(polygon[0]);
			polygon.pop_front();
		}
		Triangle *t = new Triangle(polygon[polygon.size() - 1], polygon[0], polygon[1]);
		//cout<<pts[polygon[polygon.size() - 1]].x<<","<<pts[polygon[polygon.size() - 1]].y << " " << pts[polygon[0]].x<<","<<pts[polygon[0]].y<<" "<< pts[polygon[1]].x<<","<<pts[polygon[1]].y<<endl;
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
		//std::cout << "triangle " << t->p[0] << " " << t->p[1] << " " << t->p[2] << std::endl;
		//std::cout << pts[4].x << ' ' << pts[4].y << endl;
		//std::cout << pts[3].x << ' ' << pts[3].y << endl;
		//std::cout << pts[2].x << ' ' << pts[2].y << endl;
		//std::cout << turn(pts[4], pts[3], pts[2]) << endl;
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
				Triangle *ti = t->t[(i + 1) % 3];
				t1->t[1] = ti;
				if (ti)
					ti->t[ti->get_ind(t1->p[2])] = t1;
				t1->t[2] = t;
				t2 = new Triangle(p_ind, tt->p[(j + 1) % 3], tt->p[(j + 2) % 3]);
				t2->t[0] = t;
				Triangle *tj = tt->t[(j + 1) % 3];
				t2->t[1] = tj;
				if (tj)
					tj->t[tj->get_ind(t2->p[2])] = t2;
				t2->t[2] = tt;
				t->p[(i + 1) % 3] = p_ind;
				t->t[i] = t2;
				t->t[(i + 1) % 3] = t1;
				tt->p[(j + 1) % 3] = p_ind;
				tt->t[j] = t1;
				tt->t[(j + 1) % 3] = t2;
			}
			else {
				t1 = new Triangle(p_ind, t->p[1], t->p[2]);
				Triangle *tt1 = t->t[1];
				t1->t[1] = tt1;
				if (tt1)
					tt1->t[tt1->get_ind(t->p[2])] = t1;
				t2 = new Triangle(p_ind, t->p[2], t->p[0]);
				Triangle *tt2 = t->t[2];
				t2->t[1] = tt2;
				if (tt2)
					tt2->t[tt2->get_ind(t->p[0])] = t2;
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
			if (turn(r1, r2, r4) < MyNum(0) || turn(r1, r3, r4) > MyNum(0))
				continue;
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
			else{
				std::cout << turn(r1, r2, r4) << std::endl;
				std::cout << turn(r1, r3, r4) << std::endl;
				std::cout << "--------------------------------------------" << std::endl;
				resolve_cross(con, t);
			}
			return;
		}
	}
}

void Instance::resolve_cross(std::pair<int, int> con, Triangle* t) {
	int q1 = con.first;
	int q2 = con.second;
	int i = t->get_ind(q1);
	flip(t, (i + 1) % 3);
	int r = t->p[(i + 2) % 3];
	if (t->p[(i + 2) % 3] == q2) {
		Triangle* tt = t->t[(i + 2) % 3];
		tt->t[tt->get_ind(t->p[i])] = nullptr;
		t->t[(i + 2) % 3] = nullptr;
		return;
	}
	else if (turn(pts[q2], pts[q1], pts[r]) < MyNum(0))
		return resolve_cross(con, t);
	else
		return resolve_cross(con, t->t[(i + 2) % 3]);
	// Triangle *tt = t->t[(i + 1) % 3];
	// int j = (tt->get_ind(t->p[(i + 1) % 3]) + 1) % 3;
	// int r = tt->p[j];
	// std::cout << "resolving cross" << std::endl;
	// std::cout << pts[q1] << std::endl;
	// std::cout << pts[t->p[(i+1) % 3]] << std::endl;
	// std::cout << pts[t->p[(i+2) % 3]] << std::endl;
	// std::cout << pts[r] << std::endl;
	// std::cout << pts[q2] << std::endl;
	// if (turn(pts[q1], pts[t->p[(i + 1) % 3]], pts[r]) <= MyNum(0)) {
	// 	std::cout << "flip tt1" << std::endl;
	// 	flip(tt, j);
	// 	return resolve_cross(con, t);
	// }
	// if (turn(pts[q1], pts[t->p[(i + 2) % 3]], pts[r]) >= MyNum(0)) {
	// 	std::cout << "flip tt2" << std::endl;
	// 	//std::cout << pts[tt->p[j]] << std::endl;
	// 	//std::cout << pts[tt->p[(j + 1) % 3]] << std::endl;
	// 	//std::cout << pts[tt->p[(j + 2) % 3]] << std::endl;
	// 	flip(tt, (j + 2) % 3);
	// 	return resolve_cross(con, t);
	// }
	// Triangle *ti = t->t[(i + 2) % 3];
	// Triangle *tj = tt->t[(j + 2) % 3];
	// t->p[(i + 2) % 3] = r;
	// t->t[(i + 1) % 3] = tj;
	// if (tj)
	// 	tj->t[tj->get_ind(r)] = t;
	// tt->p[(j + 2) % 3] = q1;
	// tt->t[(j + 1) % 3] = ti;
	// if (ti)
	// 	ti->t[ti->get_ind(q1)] = tt;
	// if (r==q2) {
	// 	t->t[(i + 2) % 3] = nullptr;
	// 	tt->t[(j + 2) % 3] = nullptr;
	// }
	// else {
	// 	t->t[(i + 2) % 3] = tt;
	// 	tt->t[(j + 2) % 3] = t;
	// 	if (turn(pts[q2], pts[q1], pts[r]) < MyNum(0)) {
	// 		resolve_cross(con, t);
	// 	}
	// 	else {
	// 		resolve_cross(con, tt);
	// 	}
	// }
}

void Instance::flip(Triangle* t, int i) {
	Triangle* tt = t->t[i];
	assert(tt);
	assert(tt!=t);
	int j = tt->get_ind(t->p[(i + 1) % 3]);
	int pi = t->p[(i + 2) % 3];
	int pj = tt->p[(j + 2) % 3];
	std::cout << "In flip:" << std::endl;
	std::cout << pts[pi] << std::endl;
	std::cout << pts[t->p[i]] << std::endl;
	std::cout << pts[tt->p[j]] << std::endl;
	std::cout << pts[pj] << std::endl;
	if (turn(pts[pi], pts[t->p[i]], pts[pj]) > MyNum(0) && turn(pts[pi], pts[tt->p[j]], pts[pj]) < MyNum(0)) {
		Triangle *ti = t->t[(i + 1) % 3];
		Triangle *tj = tt->t[(j + 1) % 3];
		t->p[(i + 1) % 3] = pj;
		t->t[i] = tj;
		if (tj)
			tj->t[tj->get_ind(pj)] = t;
		t->t[(i + 1) % 3] = tt;
		tt->p[(j + 1) % 3] = pi;
		tt->t[j] = ti;
		if (ti)
			ti->t[ti->get_ind(pi)] = tt;
		tt->t[(j + 1) % 3] = t;
		std::cout << "flip done" << std::endl;
		return;
	}
	if (turn(pts[pi], pts[t->p[i]], pts[pj]) <= MyNum(0)){
		std::cout << "right" << std::endl;
		Triangle *ttt = tt->t[(j + 2) % 3];
		int k = (ttt->get_ind(tt->p[j]) + 2) % 3;
		int pk = ttt->p[k];
		if (turn(pts[pi], pts[tt->p[j]], pts[pk]) >= MyNum(0)) {
			std::cout << "right-left" << std::endl;
			flip(ttt, (k + 2) % 3);
		}
		else
			flip(tt, (j + 2) % 3);
		return flip(t, i);
	}
	else {
		std::cout << "left" << std::endl;
		Triangle *ttt = tt->t[(j + 1) % 3];
		int k = (ttt->get_ind(tt->p[(j + 2) % 3]) + 2) % 3;
		int pk = ttt->p[k];
		if (turn(pts[pi], pts[t->p[i]], pts[pk]) <= MyNum(0)) {
			std::cout << "left-right" << std::endl;
			flip(ttt, k);
		}
		else
			flip(tt, (j + 1) % 3);
		return flip(t, i);
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
	return (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x);
}

std::pair<int, int> sorted_pair(int a, int b) {
	return (a > b) ? std::make_pair(b, a) : std::make_pair(a, b); 
}

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

void Instance::DrawResult(string s){
	
	MyNum minx(this->pts[0].x);
	MyNum miny(this->pts[0].y);
	MyNum maxx(this->pts[0].x);
	MyNum maxy(this->pts[0].y);
	for (int i = 0; i < this->pts.size() ; i++){
		if (minx>MyNum(this->pts[i].x)) minx=MyNum(this->pts[i].x);
		if (miny>MyNum(this->pts[i].y)) miny=MyNum(this->pts[i].y);
		if (maxx<MyNum(this->pts[i].x)) maxx=MyNum(this->pts[i].x);
		if (maxy<MyNum(this->pts[i].y)) maxy=MyNum(this->pts[i].y);
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
	for (Triangle* t : this->triangles) {
		cv::Point triangle_pt[1][3]; 
		triangle_pt[0][0] = cv::Point(minw+(int)this->pts[t->p[0]].x.toDouble()*rad, minh-(int)this->pts[t->p[0]].y.toDouble()*rad); 
		triangle_pt[0][1] = cv::Point(minw+(int)this->pts[t->p[1]].x.toDouble()*rad, minh-(int)this->pts[t->p[1]].y.toDouble()*rad); 
		triangle_pt[0][2] = cv::Point(minw+(int)this->pts[t->p[2]].x.toDouble()*rad, minh-(int)this->pts[t->p[2]].y.toDouble()*rad); 
		const cv::Point* ppt[1] = { triangle_pt[0] };
		int npt[] = { 3 };
		
		fillPoly(img, ppt, npt, 1, cv::Scalar(dis(gen), dis(gen), dis(gen)), 8);
	}

	std::set<std::pair<int, int>> const_edges;
	std::set<std::pair<int, int>> int_edges;
	for (std::pair<int, int> e : this->constraints){
		const_edges.insert(sorted_pair(e.first, e.second));
		cv::line(img, cv::Point(minw+(int)this->pts[e.first].x.toDouble()*rad,minh-(int)this->pts[e.first].y.toDouble()*rad), cv::Point(minw+(int)this->pts[e.second].x.toDouble()*rad,minh-(int)this->pts[e.second].y.toDouble()*rad), cv::Scalar(0,0,255), 2);
	}
	cout<<this->boundary.size()<<endl;
	for (int i = 1 ; i < this->boundary.size() ; i++){
		const_edges.insert(sorted_pair(this->boundary[i-1], this->boundary[i]));
		cv::line(img, cv::Point(minw+(int)this->pts[this->boundary[i-1]].x.toDouble()*rad,minh-(int)this->pts[this->boundary[i-1]].y.toDouble()*rad), cv::Point(minw+(int)this->pts[this->boundary[i]].x.toDouble()*rad,minh-(int)this->pts[this->boundary[i]].y.toDouble()*rad), cv::Scalar(255,0,0), 2);
	}
	const_edges.insert(sorted_pair(this->boundary[0], this->boundary[this->boundary.size()-1]));
	//cout<<"const edges"<<endl;
	for (std::pair<int, int> e:const_edges)
		//cout<<e.first<<" "<<e.second<<endl;
	cv::line(img, cv::Point(minw+(int)this->pts[this->boundary[0]].x.toDouble()*rad,minh-(int)this->pts[this->boundary[0]].y.toDouble()*rad), cv::Point(minw+(int)this->pts[this->boundary[this->boundary.size()-1]].x.toDouble()*rad,minh-(int)this->pts[this->boundary[this->boundary.size()-1]].y.toDouble()*rad), cv::Scalar(255,0,0), 2);
	//cout<<"new edges"<<endl;
	for (Triangle* t : this->triangles) {
		std::pair<int, int> e1 = sorted_pair(t->p[0], t->p[1]);
		std::pair<int, int> e2 = sorted_pair(t->p[1], t->p[2]);
		std::pair<int, int> e3 = sorted_pair(t->p[0], t->p[2]);
		auto cend = const_edges.end();
		auto iend = int_edges.end();
		if (const_edges.find(e1) == cend && int_edges.find(e1) == iend){
			int_edges.insert(e1);
			cv::line(img, cv::Point(minw+(int)this->pts[e1.first].x.toDouble()*rad,minh-(int)this->pts[e1.first].y.toDouble()*rad), cv::Point(minw+(int)this->pts[e1.second].x.toDouble()*rad,minh-(int)this->pts[e1.second].y.toDouble()*rad), cv::Scalar(0,0,0), 2);
		}
		if (const_edges.find(e2) == cend && int_edges.find(e2) == iend){
			int_edges.insert(e2);
			cv::line(img, cv::Point(minw+(int)this->pts[e2.first].x.toDouble()*rad,minh-(int)this->pts[e2.first].y.toDouble()*rad), cv::Point(minw+(int)this->pts[e2.second].x.toDouble()*rad,minh-(int)this->pts[e2.second].y.toDouble()*rad), cv::Scalar(0,0,0), 2);
		}
		if (const_edges.find(e3) == cend && int_edges.find(e3) == iend){
			int_edges.insert(e3);
			cv::line(img, cv::Point(minw+(int)this->pts[e3.first].x.toDouble()*rad,minh-(int)this->pts[e3.first].y.toDouble()*rad), cv::Point(minw+(int)this->pts[e3.second].x.toDouble()*rad,minh-(int)this->pts[e3.second].y.toDouble()*rad), cv::Scalar(0,0,0), 2);
		}
	}
	for (int i = 0; i < this->pts.size() ; i++){
		if (i<this->fp_ind) cv::circle(img, cv::Point(minw+(int)this->pts[i].x.toDouble()*rad,minh-(int)this->pts[i].y.toDouble()*rad),5,cv::Scalar(0,0,0),cv::FILLED);
		else cv::circle(img, cv::Point(minw+(int)this->pts[i].x.toDouble()*rad,minh-(int)this->pts[i].y.toDouble()*rad),5,cv::Scalar(255,0,0),cv::FILLED);
	}

	cv::imwrite("solutions/" + this->instance_name + "_" +s+ ".solution.png", img);
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

