#include "data.h"
#include <tuple>
#include <cstdlib>
#define IMP 100

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


long double angle(Point p1, Point p2, Point p3){
	assert(p1 != p2);
	assert(p2 != p3);
	MyNum p12x = p2.x-p1.x;
	MyNum p12y = p2.y-p1.y;
	MyNum p23x = p2.x-p3.x;
	MyNum p23y = p2.y-p3.y;
	MyNum ab = p12x * p23x + p12y * p23y;
	MyNum a = p12x * p12x + p12y * p12y;
	MyNum b = p23x * p23x + p23y * p23y;
	if (turn(p1, p2, p3) == 0)
		return (ab.den >= 0) ? -1. : 1.;
	else if (ab == MyNum(0))
		return 0.;
	long double dab = ab.toDouble();
	long double ra = std::sqrt(a.toDouble());
	long double rb = std::sqrt(b.toDouble());
	return - dab / ra / rb;
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
	this->t[0] = nullptr;
	this->t[1] = nullptr;
	this->t[2] = nullptr;
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
	if (angle(q1, q2, q3) > 0) return true;
	if (angle(q2, q3, q1) > 0) return true;
	if (angle(q3, q1, q2) > 0) return true;
	return false;
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
	else 
		return false;
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
	//int i=0;
	//DrawResult(std::to_string(i));
	for (std::pair<int, int> con : constraints){
		//i++;
		resolve_cross(con);
		//DrawResult(std::to_string(i));
	}
}

void Instance::add_steiner(Point p){
	
	pts.push_back(p);
	insert_point(pts.size()-1);
	for (std::pair<int, int> e : constraints){
		if (is_on(e, p)){
			int e1, e2 = e.first; e.second;
			constraints.insert(std::make_pair(e1, pts.size()-1));
			constraints.insert(std::make_pair(pts.size()-1, e2));
			constraints.erase(e);
		}
	}
}

void Instance::delete_steiner(Point p){

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
		while(turn(pts[polygon[polygon.size() - 1]], pts[polygon[0]], pts[polygon[1]]) <= MyNum(0)){
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
			t1->t[t1->get_ind(polygon[c])] = t2;
			t2->t[t2->get_ind(t->p[1])] = t1;
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
				// std::cout << turn(r1, r2, r4) << std::endl;
				// std::cout << turn(r1, r3, r4) << std::endl;
				// std::cout << "--------------------------------------------" << std::endl;
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
	// std::cout << "In flip:" << std::endl;
	// std::cout << pts[pi] << std::endl;
	// std::cout << pts[t->p[i]] << std::endl;
	// std::cout << pts[tt->p[j]] << std::endl;
	// std::cout << pts[pj] << std::endl;
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
		// std::cout << "flip done" << std::endl;
		return;
	}
	if (turn(pts[pi], pts[t->p[i]], pts[pj]) <= MyNum(0)){
		// std::cout << "right" << std::endl;
		Triangle *ttt = tt->t[(j + 2) % 3];
		int k = (ttt->get_ind(tt->p[j]) + 2) % 3;
		int pk = ttt->p[k];
		if (turn(pts[pi], pts[tt->p[j]], pts[pk]) >= MyNum(0)) {
			// std::cout << "right-left" << std::endl;
			flip(ttt, (k + 2) % 3);
		}
		else
			flip(tt, (j + 2) % 3);
		return flip(t, i);
	}
	else {
		// std::cout << "left" << std::endl;
		Triangle *ttt = tt->t[(j + 1) % 3];
		int k = (ttt->get_ind(tt->p[(j + 2) % 3]) + 2) % 3;
		int pk = ttt->p[k];
		if (turn(pts[pi], pts[t->p[i]], pts[pk]) <= MyNum(0)) {
			// std::cout << "left-right" << std::endl;
			flip(ttt, k);
		}
		else
			flip(tt, (j + 1) % 3);
		return flip(t, i);
	}
}

void Instance::minmax_triangulate(){
	//int cnt = 0;
	while (true) {
		long double maxang = 0.;
		Triangle *mt = nullptr;
		int i;
		for (Triangle *t : triangles) {
			long double ang = angle(pts[t->p[2]], pts[t->p[0]], pts[t->p[1]]);
			if (ang > maxang) {
				mt = t;
				maxang = ang;
				i = 0;
			}
			ang = angle(pts[t->p[0]], pts[t->p[1]], pts[t->p[2]]);
			if (ang > maxang) {
				mt = t;
				maxang = ang;
				i = 1;
			}
			ang = angle(pts[t->p[1]], pts[t->p[2]], pts[t->p[0]]);
			if (ang > maxang) {
				mt = t;
				maxang = ang;
				i = 2;
			}			
		}
		std::cout << maxang << std::endl;
		//std::cout << i << std::endl;
		//if (mt) {std::cout<<"start ear-cutting: "<<cnt<<std::endl; print_triangle(mt);}
		if (!mt || !ear_cut(mt, i)) 
			break;
		//for (Triangle *t : triangles) print_triangle(t);
		//DrawResult(to_string(cnt));
		//cnt++;
	}
}

bool Instance::ear_cut(Triangle *t, int i) {
	Point q = pts[t->p[i]];
	Point r = pts[t->p[(i + 1) % 3]];
	Point l = pts[t->p[(i + 2) % 3]];
	long double ang = angle(l, q, r);
	std::set<Triangle*> removed, inserted;
	std::vector<std::pair<Triangle*, int>> l_neis, r_neis;
	std::vector<int> l_chain, r_chain;
	std::set<std::tuple<Triangle*, int, Triangle*>> works;
	removed.insert(t);
	r_chain.push_back(t->p[i]);
	r_chain.push_back(t->p[(i + 1) % 3]);
	l_chain.push_back(t->p[i]);
	l_chain.push_back(t->p[(i + 2) % 3]);
	if (t->t[i])
		r_neis.push_back(std::make_pair(t->t[i], t->t[i]->get_ind(t->p[(i + 1) % 3])));
	else
		r_neis.push_back(std::make_pair(nullptr, 0));
	if (t->t[(i + 2) % 3])
		l_neis.push_back(std::make_pair(t->t[(i + 2) % 3], t->t[(i + 2) % 3]->get_ind(t->p[i])));
	else
		l_neis.push_back(std::make_pair(nullptr, 0));
	Triangle *tt = t->t[(i + 1) % 3];
	bool stop = false;
	Point s;
	int j;
	auto cutright = [&] () {
		if (turn(pts[r_chain[r_chain.size() - 2]], pts[r_chain[r_chain.size() - 1]], s) <= MyNum(0) || angle(pts[r_chain[r_chain.size() - 2]], pts[r_chain[r_chain.size() - 1]], s) >= ang)
			stop = true;
		else {
			//std::cout << "cutting right" << std::endl;
			Triangle *nt = new Triangle(tt->p[j], r_chain[r_chain.size() - 2], r_chain[r_chain.size() - 1]);
			inserted.insert(nt);
			nt->t[2] = r_neis.back().first;
			if (nt->t[2]) 
				works.insert(std::make_tuple(nt->t[2], r_neis.back().second, nt));
			r_neis.pop_back();
			nt->t[1] = r_neis.back().first;
			if (nt->t[1]) 
				works.insert(std::make_tuple(nt->t[1], r_neis.back().second, nt));
			r_neis.pop_back();
			r_neis.push_back(std::make_pair(nt, 0));
			r_chain.pop_back();
			//print_triangle(nt);
		}
	};
	auto cutleft = [&] () {
		if (turn(pts[l_chain[l_chain.size() - 2]], pts[l_chain[l_chain.size() - 1]], s) >= MyNum(0) || angle(pts[l_chain[l_chain.size() - 2]], pts[l_chain[l_chain.size() - 1]], s) >= ang)
			stop = true;
		else {
			//std::cout << "cutting left" << std::endl;
			Triangle *nt = new Triangle(l_chain[l_chain.size() - 1], l_chain[l_chain.size() - 2], tt->p[j]);
			inserted.insert(nt);
			nt->t[2] = l_neis.back().first;
			if (nt->t[2]) 
				works.insert(std::make_tuple(nt->t[2], l_neis.back().second, nt));
			l_neis.pop_back();
			nt->t[0] = l_neis.back().first;
			if (nt->t[0]) 
				works.insert(std::make_tuple(nt->t[0], l_neis.back().second, nt));
			l_neis.pop_back();
			l_neis.push_back(std::make_pair(nt, 1));
			l_chain.pop_back();
			//print_triangle(nt);
		}
	};
	auto abort = [&] () {
		for (Triangle* nt : inserted)
			delete nt;
	};
	while (true) {
		if (!tt) {
			abort();
			return false;
		}
		//print_triangle(t);
		//print_triangle(tt);
		stop = false;
		j = (tt->get_ind(r_chain.back()) + 1) % 3;
		//std::cout << j << std::endl;
		s = pts[tt->p[j]];
		// std::cout << q << std::endl;
		// std::cout << l << std::endl;
		// std::cout << r << std::endl;
		// std::cout << s << std::endl;
		removed.insert(tt);
		Triangle *ttt = tt->t[j];
		if (ttt)
			l_neis.push_back(std::make_pair(ttt, ttt->get_ind(tt->p[(j + 1) % 3])));
		else
			l_neis.push_back(std::make_pair(nullptr, 0));
		ttt = tt->t[(j + 2) % 3];
		if (ttt)
			r_neis.push_back(std::make_pair(ttt, ttt->get_ind(tt->p[j])));
		else
			r_neis.push_back(std::make_pair(nullptr, 0));
		if (turn(q, r, s) <= MyNum(0)) {
			while (!stop)
				cutright();
			r_chain.push_back(tt->p[j]);
			tt = l_neis.back().first;
			l_neis.pop_back();
		}
		else if (turn(q, l, s) >= MyNum(0)) {
			while (!stop)
				cutleft();
			l_chain.push_back(tt->p[j]);
			tt = r_neis.back().first;
			r_neis.pop_back();
		}
		else {
			while (!stop && r_chain.size() > 2){
				cutright();
			}
			stop = false;
			while (!stop && l_chain.size() > 2) {
				cutleft();
			}
			bool rsgn = turn(pts[r_chain[r_chain.size() - 2]], pts[r_chain[r_chain.size() - 1]], s) <= MyNum(0) || angle(pts[r_chain[r_chain.size() - 2]], pts[r_chain[r_chain.size() - 1]], s) >= ang;
			bool lsgn = turn(pts[l_chain[l_chain.size() - 2]], pts[l_chain[l_chain.size() - 1]], s) >= MyNum(0) || angle(pts[l_chain[l_chain.size() - 2]], pts[l_chain[l_chain.size() - 1]], s) >= ang;
			if (!rsgn && !lsgn)
				break;
			else if (!rsgn) {
				l = s;
				l_chain.push_back(tt->p[j]);
				tt = r_neis.back().first;
				r_neis.pop_back();
			}
			else if (!lsgn) {
				r = s;
				r_chain.push_back(tt->p[j]);
				tt = l_neis.back().first;
				l_neis.pop_back();
			}
			else {
				abort();
				return false;
			}
		}
	}
	Triangle *t1 = new Triangle(r_chain[0], r_chain[1], tt->p[j]);
	Triangle *t2 = new Triangle(tt->p[j], l_chain[1], l_chain[0]);
	t1->t[0] = r_neis[0].first;
	if (t1->t[0])
		r_neis[0].first->t[r_neis[0].second] = t1;
	t1->t[1] = r_neis[1].first;
	if (t1->t[1])
		r_neis[1].first->t[r_neis[1].second] = t1;
	t1->t[2] = t2;
	t2->t[0] = l_neis[1].first;
	if (t2->t[0])
		l_neis[1].first->t[l_neis[1].second] = t2;
	t2->t[1] = l_neis[0].first;
	if (t2->t[1])
		l_neis[0].first->t[l_neis[0].second] = t2;
	t2->t[2] = t1;
	//std::cout << "new triangles" << std::endl;
	//print_triangle(t1);
	//print_triangle(t2);
	// std::cout << "their neighbors" << std::endl;
	// if (t1->t[0])
	// 	print_triangle(t1->t[0]);
	// if (t1->t[1])
	// 	print_triangle(t1->t[1]);
	// if (t2->t[0])
	// 	print_triangle(t2->t[0]);
	// if (t2->t[1])
	// 	print_triangle(t2->t[1]);
	// std::cout << "deleted triangles" << std::endl;
	for (Triangle *dt : removed) {
		//print_triangle(dt);
		triangles.erase(dt);
		inserted.erase(dt);
		delete dt;
	}
	triangles.insert(t1);
	triangles.insert(t2);
	for (Triangle *nt : inserted)
		triangles.insert(nt);
	for (auto work : works)
		std::get<0>(work)->t[std::get<1>(work)] = std::get<2>(work);
 	return true;
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

void Instance::make_non_obtuse(Triangle *t) {
	assert(is_obtuse(t));
	int i;
	if (angle(pts[t->p[2]], pts[t->p[0]], pts[t->p[1]]) > 0.)
		i = 0;
	else if (angle(pts[t->p[0]], pts[t->p[1]], pts[t->p[2]]) > 0.)
		i = 1;
	else
		i = 2;
	Point q = pts[t->p[i]];
	Point r = pts[t->p[(i + 1) % 3]];
	Point l = pts[t->p[(i + 2) % 3]];
	std::vector<std::pair<Triangle*, int>> l_neis, r_neis;
	std::vector<int> l_chain, r_chain;
	triangles.erase(t);
	r_chain.push_back(t->p[i]);
	r_chain.push_back(t->p[(i + 1) % 3]);
	l_chain.push_back(t->p[i]);
	l_chain.push_back(t->p[(i + 2) % 3]);
	if (t->t[i])
		r_neis.push_back(std::make_pair(t->t[i], t->t[i]->get_ind(t->p[(i + 1) % 3])));
	else
		r_neis.push_back(std::make_pair(nullptr, 0));
	if (t->t[(i + 2) % 3])
		l_neis.push_back(std::make_pair(t->t[(i + 2) % 3], t->t[(i + 2) % 3]->get_ind(t->p[i])));
	else
		l_neis.push_back(std::make_pair(nullptr, 0));
	Triangle *tt = t->t[(i + 1) % 3];
	bool stop = false;
	Point s;
	int j = 0;
	auto cutright = [&] () {
		if (turn(pts[r_chain[r_chain.size() - 2]], pts[r_chain[r_chain.size() - 1]], s) <= MyNum(0) || angle(pts[r_chain[r_chain.size() - 2]], pts[r_chain[r_chain.size() - 1]], s) > 0.){
			stop = true;
		}
		else {
			Triangle *nt = new Triangle(tt->p[j], r_chain[r_chain.size() - 2], r_chain[r_chain.size() - 1]);
			//std::cout << "cutting right" << std::endl;
			triangles.insert(nt);
			nt->t[2] = r_neis.back().first;
			if (nt->t[2]) 
				nt->t[2]->t[r_neis.back().second] = nt;
			r_neis.pop_back();
			nt->t[1] = r_neis.back().first;
			if (nt->t[1]) 
				nt->t[1]->t[r_neis.back().second] = nt;
			r_neis.pop_back();
			r_neis.push_back(std::make_pair(nt, 0));
			r_chain.pop_back();
			//print_triangle(nt);
		}
	};
	auto cutleft = [&] () {
		if (turn(pts[l_chain[l_chain.size() - 2]], pts[l_chain[l_chain.size() - 1]], s) >= MyNum(0) || angle(pts[l_chain[l_chain.size() - 2]], pts[l_chain[l_chain.size() - 1]], s) > 0.) {
			stop = true;
		}
		else {
			Triangle *nt = new Triangle(l_chain[l_chain.size() - 1], l_chain[l_chain.size() - 2], tt->p[j]);
			//std::cout << "cutting left" << std::endl;
			triangles.insert(nt);
			nt->t[2] = l_neis.back().first;
			if (nt->t[2]) 
				nt->t[2]->t[l_neis.back().second] = nt;
			l_neis.pop_back();
			nt->t[0] = l_neis.back().first;
			if (nt->t[0]) 
				nt->t[0]->t[l_neis.back().second] = nt;
			l_neis.pop_back();
			l_neis.push_back(std::make_pair(nt, 1));
			l_chain.pop_back();
			//print_triangle(nt);
		}
	};
	while (true) {
		if (!tt) {
			break;
		}
		//print_triangle(t);
		//print_triangle(tt);
		stop = false;
		j = (tt->get_ind(r_chain.back()) + 1) % 3;
		//std::cout << j << std::endl;
		s = pts[tt->p[j]];
		// std::cout << q << std::endl;
		// std::cout << l << std::endl;
		// std::cout << r << std::endl;
		// std::cout << s << std::endl;
		triangles.erase(tt);
		Triangle *ttt = tt->t[j];
		if (ttt)
			l_neis.push_back(std::make_pair(ttt, ttt->get_ind(tt->p[(j + 1) % 3])));
		else
			l_neis.push_back(std::make_pair(nullptr, 0));
		ttt = tt->t[(j + 2) % 3];
		if (ttt)
			r_neis.push_back(std::make_pair(ttt, ttt->get_ind(tt->p[j])));
		else
			r_neis.push_back(std::make_pair(nullptr, 0));
		if (turn(q, r, s) <= MyNum(0)) {
			while (!stop)
				cutright();
			r_chain.push_back(tt->p[j]);
			tt = l_neis.back().first;
			l_neis.pop_back();
		}
		else if (turn(q, l, s) >= MyNum(0)) {
			while (!stop)
				cutleft();
			l_chain.push_back(tt->p[j]);
			tt = r_neis.back().first;
			r_neis.pop_back();
		}
		else {
			while (!stop && r_chain.size() > 2){
				cutright();
			}
			stop = false;
			while (!stop && l_chain.size() > 2) {
				cutleft();
			}
			bool rsgn = turn(pts[r_chain[r_chain.size() - 2]], pts[r_chain[r_chain.size() - 1]], s) <= MyNum(0) || angle(pts[r_chain[r_chain.size() - 2]], pts[r_chain[r_chain.size() - 1]], s) > 0.;
			bool lsgn = turn(pts[l_chain[l_chain.size() - 2]], pts[l_chain[l_chain.size() - 1]], s) >= MyNum(0) || angle(pts[l_chain[l_chain.size() - 2]], pts[l_chain[l_chain.size() - 1]], s) > 0.;
			if (!rsgn && !lsgn){
				Triangle *t1 = new Triangle(r_chain[0], r_chain[1], tt->p[j]);
				Triangle *t2 = new Triangle(tt->p[j], l_chain[1], l_chain[0]);
				t1->t[0] = r_neis[0].first;
				if (t1->t[0])
					r_neis[0].first->t[r_neis[0].second] = t1;
				t1->t[1] = r_neis[1].first;
				if (t1->t[1])
					r_neis[1].first->t[r_neis[1].second] = t1;
				t1->t[2] = t2;
				t2->t[0] = l_neis[1].first;
				if (t2->t[0])
					l_neis[1].first->t[l_neis[1].second] = t2;
				t2->t[1] = l_neis[0].first;
				if (t2->t[1])
					l_neis[0].first->t[l_neis[0].second] = t2;
				t2->t[2] = t1;
				//std::cout << "new triangles" << std::endl;
				//print_triangle(t1);
				//print_triangle(t2);
				// std::cout << "their neighbors" << std::endl;
				// if (t1->t[0])
				// 	print_triangle(t1->t[0]);
				// if (t1->t[1])
				// 	print_triangle(t1->t[1]);
				// if (t2->t[0])
				// 	print_triangle(t2->t[0]);
				// if (t2->t[1])
				// 	print_triangle(t2->t[1]);
				// std::cout << "deleted triangles" << std::endl;
				// for (Triangle *dt : removed) {
				// 	//print_triangle(dt);
				// 	triangles.erase(dt);
				// 	delete dt;
				// }
				triangles.insert(t1);
				triangles.insert(t2);
				return;			
			}
			else if (!rsgn) {
				l = s;
				l_chain.push_back(tt->p[j]);
				tt = r_neis.back().first;
				r_neis.pop_back();
			}
			else if (!lsgn) {
				r = s;
				r_chain.push_back(tt->p[j]);
				tt = l_neis.back().first;
				l_neis.pop_back();
			}
			else {
				r_chain.push_back(tt->p[j]);
				tt = l_neis.back().first;
				j = l_neis.back().second;
				l_neis.pop_back();
				break;
			}
		}
	}
	std::cout << r_chain.size() << ' ' << l_chain.size() << std::endl;
	int ri = 1;
	for (; ri < r_chain.size() - 1; ri++) {
		if (turn(pts[r_chain[ri - 1]], pts[r_chain[ri]], pts[r_chain[ri + 1]]) <= MyNum(0)) 
			break;
	}
	int li = 1;
	for (; li < l_chain.size() - 1; li++) {
		if (turn(pts[l_chain[li - 1]], pts[l_chain[li]], pts[l_chain[li + 1]]) >= MyNum(0))
			break;
	}
	std::cout << ri << ' ' << li << std::endl;
	while (turn(pts[l_chain[li]], pts[r_chain[ri]], pts[r_chain[ri - 1]]) >= MyNum(0))
		li--;
	while (turn(pts[l_chain[li-1]], pts[l_chain[li]], pts[r_chain[ri]]) >= MyNum(0))
		ri--;
	std::cout << ri << ' ' << li << std::endl;
	if (ri < r_chain.size() - 1 || li < l_chain.size() - 1) {
		std::deque<int> farp;
		for (int ind = ri; ind < r_chain.size(); ind++)
			farp.push_back(r_chain[ind]);
		for (int ind = l_chain.size() - 1; ind >= li; ind--)
			farp.push_back(l_chain[ind]); 
		std::cout << farp.size() << std::endl;
		triangulate_polygon(farp);
		if (tt) {
			Triangle *ttt = find_triangle(r_chain.back(), l_chain.back());
			ttt->t[ttt->get_ind(r_chain.back())] = tt;
			tt->t[j] = ttt;
		}
		std::cout << "cutting done" << std::endl;
		while (r_chain.size() - 1 > ri) {
			Triangle *ttt = find_triangle(r_chain[r_chain.size() - 2], r_chain.back());
			ttt->t[ttt->get_ind(r_chain[r_chain.size() - 2])] = r_neis.back().first;
			if (r_neis.back().first)
				r_neis.back().first->t[r_neis.back().second] = ttt;
			r_chain.pop_back();
			r_neis.pop_back();
		}
		std::cout << "rchain done" << std::endl;
		while (l_chain.size() - 1 > li) {
			Triangle *ttt = find_triangle(l_chain.back(), l_chain[l_chain.size() - 2]);
			ttt->t[ttt->get_ind(l_chain.back())] = l_neis.back().first;
			if (l_neis.back().first)
				l_neis.back().first->t[l_neis.back().second] = ttt;
			l_chain.pop_back();
			l_neis.pop_back();
		}
		std::cout << "lchain done" << std::endl;
		tt = find_triangle(l_chain.back(), r_chain.back());
		j = tt->get_ind(l_chain.back());
	}
	bool flag = (l_chain.size() == 2 && angle(pts[t->p[i]], pts[l_chain[1]], pts[r_chain.back()]) < 0.);
	flag = flag || (r_chain.size() == 2 && angle(pts[t->p[i]], pts[r_chain[1]], pts[l_chain.back()]) < 0.);
	std::cout << flag << std::endl;
	if (flag) {
		if (!tt) {
			std::vector<Point> cands;
			std::pair<int, int> tt_e = std::make_pair(l_chain.back(), r_chain.back());
			Point pp = projection(pts[t->p[i]], pts[l_chain.back()], pts[r_chain.back()]);
			if (is_on(tt_e, pp)) cands.push_back(pp);
			if (l_neis[0].first || l_chain.size() > 2) {
				std::cout << pts[r_chain[1]] << ' ' << pts[t->p[i]] << ' ' << pts[l_chain.back()] << ' ' << pts[r_chain.back()] << std::endl;
				Point lp = right_angle_point(pts[r_chain[1]], pts[t->p[i]], pts[l_chain.back()], pts[r_chain.back()]);
				if (is_on(tt_e, lp)) cands.push_back(lp);
			}
			if (r_neis[0].first || r_chain.size() > 2) {
				Point rp = right_angle_point(pts[l_chain[1]], pts[t->p[i]], pts[l_chain.back()], pts[r_chain.back()]);
				if (is_on(tt_e, rp)) cands.push_back(rp);
			}
			if (cands.size() == 0) {
				Triangle *nt = new Triangle(t->p[i], r_chain.back(), l_chain.back());
				triangles.insert(nt);
				int k;
				if (l_chain.size() == 2) {
					nt->t[2] = l_neis.back().first;
					if (nt->t[2]) nt->t[2]->t[l_neis.back().second] = nt;
					l_neis.pop_back();
					k = 0;
					l_chain.pop_back();
				}
				else {
					nt->t[0] = r_neis.back().first;
					if (nt->t[0]) nt->t[0]->t[r_neis.back().second] = nt;
					r_neis.pop_back();
					k = 2;
					r_chain.pop_back();
				}
				std::deque<int> remaining;
				for (int ind = 0; ind < r_chain.size(); ind++) remaining.push_back(r_chain[ind]);
				for (int ind = l_chain.size() - 1; ind > 0; ind--) remaining.push_back(l_chain[ind]);
				triangulate_polygon(remaining);
				Triangle *ttt = find_triangle(r_chain.back(), l_chain.back());
				nt->t[k] = ttt;
				ttt->t[ttt->get_ind(r_chain.back())] = nt;
				for (int ind = 0; ind < r_chain.size() - 1; ind++) {
					Triangle *tttt = find_triangle(r_chain[ind], r_chain[ind + 1]);
					int l = tttt->get_ind(r_chain[ind]);
					tttt->t[l] = r_neis[ind].first;
					if (r_neis[ind].first) r_neis[ind].first->t[r_neis[ind].second] = tttt;
				}
				for (int ind = 0; ind < l_chain.size() - 1; ind++) {
					Triangle *tttt = find_triangle(l_chain[ind + 1], l_chain[ind]);
					int l = tttt->get_ind(l_chain[ind + 1]);
					tttt->t[l] = l_neis[ind].first;
					if (l_neis[ind].first) l_neis[ind].first->t[l_neis[ind].second] = tttt;
				}
			}
			else {
				Point stp = cands[std::rand() % cands.size()];
				insert_point_on(std::make_pair(r_chain.back(), l_chain.back()), stp);
				r_chain.push_back(pts.size() - 1);
				std::deque<int> remaining;
				for (int ind = 0; ind < r_chain.size(); ind++) remaining.push_back(r_chain[ind]);
				for (int ind = l_chain.size() - 1; ind > 0; ind--) remaining.push_back(l_chain[ind]);
				for (int asdf : remaining) std::cout << asdf << ' ';
				std::cout << std::endl;
				std::cout << l_chain.size() << ' ' << r_chain.size() << std::endl;
				std::cout << l_neis.size() << ' ' << r_neis.size() << std::endl;
				triangulate_polygon(remaining);
				//for (auto asdf : triangles) print_triangle(asdf);
				for (int ind = 0; ind < r_chain.size() - 2; ind++) {
					Triangle *tttt = find_triangle(r_chain[ind], r_chain[ind + 1]);
					int l = tttt->get_ind(r_chain[ind]);
					tttt->t[l] = r_neis[ind].first;
					if (r_neis[ind].first) r_neis[ind].first->t[r_neis[ind].second] = tttt;
				}
				for (int ind = 0; ind < l_chain.size() - 1; ind++) {
					Triangle *tttt = find_triangle(l_chain[ind + 1], l_chain[ind]);
					int l = tttt->get_ind(l_chain[ind + 1]);
					tttt->t[l] = l_neis[ind].first;
					if (l_neis[ind].first) l_neis[ind].first->t[l_neis[ind].second] = tttt;
				}
			}
			return;
		}
		else if (angle(pts[tt->p[(j + 1) % 3]], pts[tt->p[j]], pts[tt->p[(j + 2) % 3]]) > 0. || angle(pts[tt->p[j]], pts[tt->p[(j + 1) % 3]], pts[tt->p[(j + 2) % 3]]) > 0.) {
			std::deque<int> remaining;
			for (int ind = 0; ind < r_chain.size(); ind++) remaining.push_back(r_chain[ind]);
			for (int ind = l_chain.size() - 1; ind > 0; ind--) remaining.push_back(l_chain[ind]);
			triangulate_polygon(remaining);
			Triangle *ttt = find_triangle(r_chain.back(), l_chain.back());
			tt->t[j] = ttt;
			ttt->t[ttt->get_ind(r_chain.back())] = tt;
			for (int ind = 0; ind < r_chain.size() - 1; ind++) {
				Triangle *tttt = find_triangle(r_chain[ind], r_chain[ind + 1]);
				int l = tttt->get_ind(r_chain[ind]);
				tttt->t[l] = r_neis[ind].first;
				if (r_neis[ind].first) r_neis[ind].first->t[r_neis[ind].second] = tttt;
			}
			for (int ind = 0; ind < l_chain.size() - 1; ind++) {
				Triangle *tttt = find_triangle(l_chain[ind + 1], l_chain[ind]);
				int l = tttt->get_ind(l_chain[ind + 1]);
				tttt->t[l] = l_neis[ind].first;
				if (l_neis[ind].first) l_neis[ind].first->t[l_neis[ind].second] = tttt;
			}
			make_non_obtuse(tt);
			return;
		}
	}
	//we got conv polygon
	std::vector<Point> cands;
	r_neis.push_back(std::make_pair(tt, j));
	while (l_chain.size() > 1) {
		r_chain.push_back(l_chain.back());
		l_chain.pop_back();
		r_neis.push_back(l_neis.back());
		l_neis.pop_back();
	}
	cands.push_back(projection(pts[r_chain[0]], pts[r_chain[1]], pts[r_chain.back()]));
	for (Point pp : intersections_of_orthogonals(pts[r_chain[0]], pts[r_chain[1]], pts[r_chain[0]], pts[r_chain.back()])) {
		bool in = turn(pts[r_chain.back()], pts[r_chain[0]], pp) > MyNum(0);
		if (in) {
			for (int ind = 0; ind < r_chain.size() - 1; ind++) {
				if (turn(pts[r_chain[ind]], pts[r_chain[ind + 1]], pp) <= MyNum(0)) {
					in = false;
					break;
				}
			}
		}
		if (in) cands.push_back(pp);
	}
	r_chain.push_back(r_chain[0]);
	for (int ind = 1; ind < r_chain.size() - 1; ind++) {
		cands.push_back(projection(pts[r_chain[ind]], pts[r_chain[ind - 1]], pts[r_chain[ind + 1]]));
		for (Point pp : intersections_of_orthogonals(pts[r_chain[ind - 1]], pts[r_chain[ind]], pts[r_chain[ind]], pts[r_chain[ind + 1]])) {
			bool in = true;
			for (int ii = 0; ii < r_chain.size() - 1; ii++) {
				if (turn(pts[r_chain[ii]], pts[r_chain[ii + 1]], pp) <= MyNum(0)) {
					in = false;
					break;
				}
			}
			if (in) cands.push_back(pp);
		}
	}
	for (int ii = 0; ii < r_chain.size() - 1; ii++) {
		for (int jj = ii + 2; jj < r_chain.size() - 1; jj++) {
			if (ii==0 && jj==r_chain.size() - 2) continue;
			for (Point pp : intersections_of_orthogonals(pts[r_chain[ii]], pts[r_chain[ii + 1]], pts[r_chain[jj]], pts[r_chain[jj + 1]])) {
				bool in = true;
				for (int kk = 0; kk < r_chain.size() - 1; kk++) {
					if (turn(pts[r_chain[kk]], pts[r_chain[kk + 1]], pp) <= MyNum(0)) {
						in = false;
						break;
					}
				}
				if (in) cands.push_back(pp);
			}
			for (Point pp : intersections_of_disks(midpoint(pts[r_chain[ii]], pts[r_chain[ii + 1]]), sqdist(pts[r_chain[ii]], pts[r_chain[ii + 1]]) / MyNum(4), midpoint(pts[r_chain[jj]], pts[r_chain[jj + 1]]), sqdist(pts[r_chain[jj]], pts[r_chain[jj + 1]]) / MyNum(4))) {
				bool in = true;
				for (int kk = 0; kk < r_chain.size() - 1; kk++) {
					if (turn(pts[r_chain[kk]], pts[r_chain[kk + 1]], pp) <= MyNum(0)) {
						in = false;
						break;
					}
				}
				if (in) cands.push_back(pp);
			}
		}
	}
	std::vector<Point> bcands;
	int bscore = 0;
	for (Point pp : cands) {
		int score = 0;
		for (int ind = 0; ind < r_chain.size() - 1; ind++) {
			if (angle(pts[r_chain[ind]], pts[r_chain[ind + 1]], pp) <= 0. && angle(pts[r_chain[ind]], pp, pts[r_chain[ind + 1]]) <= 0. && angle(pts[r_chain[ind + 1]], pts[r_chain[ind]], pp) <= 0.) score++;
		}
		if (score < bscore) continue;
		if (score > bscore) {
			bscore = score;
			bcands.clear();
		}
		bcands.push_back(pp);
	}
	Point stp = bcands[std::rand() % bcands.size()];
	pts.push_back(stp);
	std::cout << "new point: " << stp << std::endl;
	Triangle *t0 = new Triangle(pts.size() - 1, r_chain[0], r_chain[1]);
	triangles.insert(t0);
	t0->t[1] = r_neis[0].first;
	if (r_neis[0].first) r_neis[0].first->t[r_neis[0].second] = t0;
	Triangle *pt = t0;
	for (int ind = 1; ind < r_chain.size() - 1; ind++) {
		Triangle *nt = new Triangle(pts.size() - 1, r_chain[ind], r_chain[ind + 1]);
		triangles.insert(nt);
		nt->t[1] = r_neis[ind].first;
		if (r_neis[ind].first) r_neis[ind].first->t[r_neis[ind].second] = nt;
		nt->t[0] = pt;
		pt->t[2] = nt;
		pt = nt;
	}
	pt->t[2] = t0;
	t0->t[0] = pt;
}

void Instance::insert_point_on(std::pair<int, int> e, Point p) {
	assert(is_on(e, p));
	pts.push_back(p);
	std::cout << "new point: " << p << std::endl;
	int ind = pts.size() - 1;
	bool inserted = false;
	if ((e.first == boundary.back() && e.second == boundary[0]) || (e.first == boundary[0] && e.second == boundary.back())) {
		boundary.push_back(ind);
		inserted = true;
	}
	else {
		for (int i = 0; i < boundary.size() - 1; i++) {
			if ((e.first == boundary[i] && e.second == boundary[i + 1]) || (e.first == boundary[i + 1] && e.second == boundary[i])) {
				boundary.insert(boundary.begin() + i + 1, ind);
				inserted = true;
				break;
			}
		}
	}
	if (!inserted) {
		for (std::pair<int, int> cons : constraints) {
			if (cons == e || (cons.first == e.second && cons.second == e.first)) {
				int i1 = cons.first;
				int i2 = cons.second;
				constraints.erase(cons);
				constraints.insert(std::make_pair(i1, ind));
				constraints.insert(std::make_pair(i2, ind));
				break;
			}
		}
	}
	Triangle *t1 = find_triangle(e.first, e.second);
	Triangle *t2 = find_triangle(e.second, e.first);
	if (t1) {
		int i = t1->get_ind(e.first);
		Triangle *nt = new Triangle(ind, t1->p[(i + 1) % 3], t1->p[(i + 2) % 3]);
		Triangle *ti1 = t1->t[(i + 1) % 3];
		nt->t[1] = ti1;
		ti1->t[ti1->get_ind(t1->p[(i + 2) % 3])] = nt;
		nt->t[2] = t1;
		t1->t[(i + 1) % 3] = nt;
		t1->p[(i + 1) % 3] = ind;
		triangles.insert(nt);
	}
	if (t2) {
		int i = t2->get_ind(e.second);
		Triangle *nt = new Triangle(ind, t2->p[(i + 1) % 3], t2->p[(i + 2) % 3]);
		Triangle *ti1 = t2->t[(i + 1) % 3];
		nt->t[1] = ti1;
		ti1->t[ti1->get_ind(t2->p[(i + 2) % 3])] = nt;
		nt->t[2] = t2;
		t2->t[(i + 1) % 3] = nt;
		t2->p[(i + 1) % 3] = ind;
		triangles.insert(nt);
	}
}

void Instance::step() {
	std::vector<Triangle*> obtt;
	for (Triangle* t : triangles) {
		if (is_obtuse(t)) obtt.push_back(t);
	}
	if (obtt.empty()) std::cout << "Done!" << std::endl;
	else {
		Triangle *target = obtt[std::rand() % obtt.size()];
		std::cout << "Try a step" << std::endl;
		print_triangle(target);
		make_non_obtuse(target);
		minmax_triangulate();
	}
}

void Instance::print_triangle(Triangle* t) {
	std::cout << "Triangle: " << t << std::endl;
	std::cout << t->p[0] << ':' << pts[t->p[0]] << std::endl;
	std::cout << t->p[1] << ':' << pts[t->p[1]] << std::endl;
	std::cout << t->p[2] << ':' << pts[t->p[2]] << std::endl;
	std::cout << t->t[0] << std::endl;
	std::cout << t->t[1] << std::endl;
	std::cout << t->t[2] << std::endl;
}

void Instance::DrawResult(std::string s){
	
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

MyNum turn(Point p1, Point p2, Point p3){
	return (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x);
}

Point projection(Point p, Point q1, Point q2) {
	if (q1.x == q2.x) return Point(q1.x, p.y);
	if (q1.y == q2.y) return Point(p.x, q1.y);
	MyNum s1 = (q2.y - q1.y) / (q2.x - q1.x);
	MyNum b1 = q1.y - s1 * q1.x;
	MyNum s2 = MyNum(-1) / s1;
	MyNum b2 = p.y - s2 * p.x;
	MyNum rx = (b2 - b1) / (s1 - s2);
	MyNum ry = rx * s1 + b1;
	return Point(rx, ry);
}

Point right_angle_point(Point p1, Point p2, Point p3, Point p4) {
	if (p3.x == p4.x) {
		if (p1.y == p2.y) return Point(0, 0);
		if (p1.x == p2.x) return Point(p3.x, p2.y);
		MyNum s = (p1.x - p2.x) / (p2.y - p1.y);
		MyNum b = p2.y - s * p2.x;
		MyNum qy = s * p3.x + b;
		return Point(p3.x, qy);
	}
	else if (p1.y == p2.y) {
		MyNum s = (p3.y - p4.y) / (p3.x - p4.x);
		MyNum b = p3.y - s * p3.x;
		MyNum qy = s * p2.x + b;
		return Point(p2.x, qy);
	}
	else {
		MyNum s1 = (p3.y - p4.y) / (p3.x - p4.x);
		std::cout << s1 << std::endl;
		MyNum s2 = (p1.x - p2.x) / (p2.y - p1.y);
		std::cout << s2 << std::endl;
		if (s1 == s2) return Point(0, 0);
		MyNum b1 = p3.y - s1 * p3.x;
		std::cout << b1 << std::endl;
		MyNum b2 = p2.y - s2 * p2.x;
		std::cout << b2 << std::endl;
		MyNum qx = (b2 - b1) / (s1 - s2);
		std::cout << qx << std::endl;
		MyNum qy = qx * s1 + b1;
		std::cout << qy << std::endl;
		return Point(qx, qy);
	}
}

Point midpoint(Point p, Point q) {
	return Point((p.x + q.x) / MyNum(2), (p.y + q.y) / MyNum(2));
}

std::vector<Point> intersections_of_orthogonals(Point p1, Point p2, Point p3, Point p4) {
	std::vector<Point> res;
	if (p1.y == p2.y) {
		if (p3.y == p4.y) {
			return res;
		}
		MyNum s = (p4.x - p3.x) / (p3.y - p4.y);
		MyNum b3 = p3.y - s * p3.x;
		MyNum b4 = p4.y - s * p4.x;
		res.push_back(Point(p1.x, s * p1.x + b3));
		res.push_back(Point(p1.x, s * p1.x + b4));
		res.push_back(Point(p2.x, s * p2.x + b3));
		res.push_back(Point(p2.x, s * p2.x + b4));
		return res;
	}
	else if (p3.y == p4.y) return intersections_of_orthogonals(p3, p4, p1, p2);
	else {
		MyNum s12 = (p2.x - p1.x) / (p1.y - p2.y);
		MyNum s34 = (p4.x - p3.x) / (p3.y - p4.y);
		if (s12 == s34) {
			return res;
		}
		MyNum b1 = p1.y - s12 * p1.x;
		MyNum b2 = p2.y - s12 * p2.x;
		MyNum b3 = p3.y - s34 * p3.x;
		MyNum b4 = p4.y - s34 * p4.x;
		MyNum x13 = (b1 - b3) / (s34 - s12);
		res.push_back(Point(x13, s12 * x13 + b1));
		MyNum x23 = (b2 - b3) / (s34 - s12);
		res.push_back(Point(x23, s12 * x23 + b2));
		MyNum x14 = (b1 - b4) / (s34 - s12);
		res.push_back(Point(x14, s12 * x14 + b1));
		MyNum x24 = (b2 - b4) / (s34 - s12);
		res.push_back(Point(x24, s12 * x24 + b2));
		return res;
	}
}

std::vector<Point> intersections_of_disks(Point p1, MyNum r1, Point p2, MyNum r2) {
	std::vector<Point> res;
	if (p1.y == p2.y) {
		if (p1.x == p2.x) return res;
		MyNum qx = (p1.x + p2.x + (r2 - r1) / (p1.x - p2.x)) / MyNum(2);
		MyNum sqrhs = r1 - (qx - p1.x) * (qx - p1.x);
		if (sqrhs < MyNum(0)) return res;
		long double drhs = std::sqrt(sqrhs.toDouble());
		MyNum rhs1 = MyNum((int) drhs * IMP, IMP);
		MyNum rhs2 = MyNum((int) drhs * IMP + 1, IMP);
		res.push_back(Point(qx, p1.y + rhs1));
		res.push_back(Point(qx, p1.y + rhs2));
		res.push_back(Point(qx, p1.y - rhs1));
		res.push_back(Point(qx, p1.y - rhs2));
		return res;
	}
	MyNum s = (p2.x - p1.x) / (p1.y - p2.y);
	MyNum bb = (p1.x * p1.x + p1.y * p1.y - p2.x * p2.x - p2.y * p2.y - r1 + r2) / (p1.y - p2.y) / MyNum(2);
	MyNum a = s * s + MyNum(1);
	MyNum b = MyNum(2) * (-p1.x + s * (bb - p1.y));
	MyNum c = p1.x * p1.x + (bb - p1.y) * (bb - p1.y) - r1;
	MyNum inroot = b * b - MyNum(4) * a * c;
	if (inroot < MyNum(0)) return res;
	long double db24ac = std::sqrt(inroot.toDouble());
	MyNum root1 = MyNum((int) db24ac * IMP, IMP);
	MyNum root2 = MyNum((int) db24ac * IMP + 1, IMP);
	MyNum x1 = (-b + root1) / a / MyNum(2);
	MyNum x2 = (-b + root2) / a / MyNum(2);
	MyNum x3 = (-b - root1) / a / MyNum(2);
	MyNum x4 = (-b - root2) / a / MyNum(2);
	for (MyNum x: {x1, x2, x3, x4}) res.push_back(Point(x, s * x + bb));
	return res;
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

