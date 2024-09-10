#include "MyInstance.h"

#include <assert.h>
#include <tuple>
#include <random>

#include "opencv2/opencv.hpp"
#include "utility.h"

using namespace std;

Instance::Instance() {
	this->fp_ind = 0;
}

Instance::Instance(int _fp_ind, std::vector<Point> _pts, std::deque<int> _boundary, std::set<std::pair<int, int>> _constraints) {
	this->fp_ind = _fp_ind;
	this->pts = _pts;
	this->boundary = _boundary;
	this->constraints = _constraints;
}

bool Instance::is_obtuse(Triangle* t) {
	Point q1 = pts[t->p[0]];
	Point q2 = pts[t->p[1]];
	Point q3 = pts[t->p[2]];
	if (angle(q1, q2, q3) > 0) return false;
	if (angle(q2, q3, q1) > 0) return false;
	if (angle(q3, q1, q2) > 0) return false;
	return true;
}

bool Instance::is_on(std::pair<int, int> e, Point p) {
	Point q1 = pts[e.first];
	Point q2 = pts[e.second];
	if (turn(q1, q2, p) == MyNum(0)) {
		if (q1.x == q2.x) {
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

bool Instance::is_in(Triangle* t, Point p) {
	Point q1 = pts[t->p[0]];
	Point q2 = pts[t->p[1]];
	Point q3 = pts[t->p[2]];
	MyNum zero(0);
	return (turn(q1, q2, p) >= zero) && (turn(q2, q3, p) >= zero) && (turn(q3, q1, p) >= zero);
}

void Instance::triangulate() {
	std::vector<bool> check(pts.size(), false);
	triangulate_polygon(this->boundary);
	//std::cout << boundary.size() << " " << triangles.size() << std::endl;
	for (int d : boundary)
		check[d] = true;
	for (int i = 0; i < pts.size(); i++){
		if (!check[i]) {
			insert_point(i);
			//std::cout << "inserted " << i << ": " << triangles.size() << std::endl;
		}
	}
	//int i=0;
	//DrawResult(std::to_string(i));
	for (std::pair<int, int> con : constraints) {
		//i++;
		resolve_cross(con);
		//DrawResult(std::to_string(i));
	}
}

void Instance::add_steiner(Point p) {

	pts.push_back(p);
	insert_point(pts.size() - 1);
	for (std::pair<int, int> e : constraints) {
		if (is_on(e, p)) {
			int e1, e2 = e.first; e.second;
			constraints.insert(std::make_pair(e1, pts.size() - 1));
			constraints.insert(std::make_pair(pts.size() - 1, e2));
			constraints.erase(e);
		}
	}
}

void Instance::delete_steiner(Point p) {

}

void Instance::triangulate_polygon(std::deque<int> polygon) {
	if (polygon.size() == 3) {
		Triangle* t = new Triangle(polygon[0], polygon[1], polygon[2]);
		t->t[0] = nullptr;
		t->t[1] = nullptr;
		t->t[2] = nullptr;
		triangles.insert(t);
	}
	else {
		while (turn(pts[polygon[polygon.size() - 1]], pts[polygon[0]], pts[polygon[1]]) <= MyNum(0)) {
			polygon.push_back(polygon[0]);
			polygon.pop_front();
		}
		Triangle* t = new Triangle(polygon[polygon.size() - 1], polygon[0], polygon[1]);
		//cout<<pts[polygon[polygon.size() - 1]].x<<","<<pts[polygon[polygon.size() - 1]].y << " " << pts[polygon[0]].x<<","<<pts[polygon[0]].y<<" "<< pts[polygon[1]].x<<","<<pts[polygon[1]].y<<endl;
		t->t[0] = nullptr;
		t->t[1] = nullptr;
		t->t[2] = nullptr;
		int c = -1;
		Point q = pts[polygon[0]];
		MyNum d1 = sqdist(q, pts[t->p[0]]);
		MyNum d2 = sqdist(q, pts[t->p[2]]);
		MyNum cdist = (d1 > d2) ? d1 : d2;
		for (int i = 2; i < polygon.size() - 1; i++) {
			if (is_in(t, pts[polygon[i]])) {
				MyNum d = sqdist(q, pts[polygon[i]]);
				if (d < cdist) {
					cdist = d;
					c = i;
				}
			}
		}
		if (c == -1) {
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
			Triangle* t1 = find_triangle(polygon[c], t->p[1]);
			triangulate_polygon(poly2);
			Triangle* t2 = find_triangle(t->p[1], polygon[c]);
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
		if (is_in(t, q)) {
			Triangle* t1, * t2;
			Triangle* tt = nullptr;
			bool on_edge = false;
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
			if (on_edge && tt) {
				if (t == tt->t[0])
					j = 0;
				else if (t == tt->t[1])
					j = 1;
				else
					j = 2;
				t1 = new Triangle(p_ind, t->p[(i + 1) % 3], t->p[(i + 2) % 3]);
				t1->t[0] = tt;
				Triangle* ti = t->t[(i + 1) % 3];
				t1->t[1] = ti;
				if (ti)
					ti->t[ti->get_ind(t1->p[2])] = t1;
				t1->t[2] = t;
				t2 = new Triangle(p_ind, tt->p[(j + 1) % 3], tt->p[(j + 2) % 3]);
				t2->t[0] = t;
				Triangle* tj = tt->t[(j + 1) % 3];
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
			else if (on_edge) {
				t1 = new Triangle(p_ind, t->p[(i + 1) % 3], t->p[(i + 1) % 3]);
				t1->t[0] = tt;
				Triangle* ti = t->t[(i + 1 % 3)];
				t1->t[1] = ti;
				if (ti)
					ti->t[ti->get_ind(t1->p[2])] = t1;
				t1->t[2] = t;
				t->p[(i + 1) % 3] = p_ind;
				t->t[i] = tt;
				t->t[(i + 1) % 3] = t1;
			}
			else {
				t1 = new Triangle(p_ind, t->p[1], t->p[2]);
				Triangle* tt1 = t->t[1];
				t1->t[1] = tt1;
				if (tt1)
					tt1->t[tt1->get_ind(t->p[2])] = t1;
				t2 = new Triangle(p_ind, t->p[2], t->p[0]);
				Triangle* tt2 = t->t[2];
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
	for (Triangle* t : triangles) {
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
				Triangle* tt = t->t[i];
				t->t[i] = nullptr;
				int j = tt->get_ind(q2);
				tt->t[j] = nullptr;
			}
			else if (r3 == r4) {
				Triangle* tt = t->t[(i + 2) % 3];
				t->t[(i + 2) % 3] = nullptr;
				int j = tt->get_ind(q1);
				tt->t[j] = nullptr;
			}
			else {
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
	assert(tt != t);
	int j = tt->get_ind(t->p[(i + 1) % 3]);
	int pi = t->p[(i + 2) % 3];
	int pj = tt->p[(j + 2) % 3];
	// std::cout << "In flip:" << std::endl;
	// std::cout << pts[pi] << std::endl;
	// std::cout << pts[t->p[i]] << std::endl;
	// std::cout << pts[tt->p[j]] << std::endl;
	// std::cout << pts[pj] << std::endl;
	if (turn(pts[pi], pts[t->p[i]], pts[pj]) > MyNum(0) && turn(pts[pi], pts[tt->p[j]], pts[pj]) < MyNum(0)) {
		Triangle* ti = t->t[(i + 1) % 3];
		Triangle* tj = tt->t[(j + 1) % 3];
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
	if (turn(pts[pi], pts[t->p[i]], pts[pj]) <= MyNum(0)) {
		// std::cout << "right" << std::endl;
		Triangle* ttt = tt->t[(j + 2) % 3];
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
		Triangle* ttt = tt->t[(j + 1) % 3];
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

void Instance::minmax_triangulate() {
	//int cnt = 0;
	while (true) {
		long double maxang = 0.;
		Triangle* mt = nullptr;
		int i;
		for (Triangle* t : triangles) {
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
		//std::cout << maxang << std::endl;
		//std::cout << i << std::endl;
		//if (mt) {std::cout<<"start ear-cutting: "<<cnt<<std::endl; print_triangle(mt);}
		if (!mt || !ear_cut(mt, i))
			break;
		//for (Triangle *t : triangles) print_triangle(t);
		//DrawResult(to_string(cnt));
		//cnt++;
	}
}

bool Instance::ear_cut(Triangle* t, int i) {
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
	Triangle* tt = t->t[(i + 1) % 3];
	bool stop = false;
	Point s;
	int j;
	auto cutright = [&]() {
		if (turn(pts[r_chain[r_chain.size() - 2]], pts[r_chain[r_chain.size() - 1]], s) <= MyNum(0) || angle(pts[r_chain[r_chain.size() - 2]], pts[r_chain[r_chain.size() - 1]], s) >= ang)
			stop = true;
		else {
			//std::cout << "cutting right" << std::endl;
			Triangle* nt = new Triangle(tt->p[j], r_chain[r_chain.size() - 2], r_chain[r_chain.size() - 1]);
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
	auto cutleft = [&]() {
		if (turn(pts[l_chain[l_chain.size() - 2]], pts[l_chain[l_chain.size() - 1]], s) >= MyNum(0) || angle(pts[l_chain[l_chain.size() - 2]], pts[l_chain[l_chain.size() - 1]], s) >= ang)
			stop = true;
		else {
			//std::cout << "cutting left" << std::endl;
			Triangle* nt = new Triangle(l_chain[l_chain.size() - 1], l_chain[l_chain.size() - 2], tt->p[j]);
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
	auto abort = [&]() {
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
		Triangle* ttt = tt->t[j];
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
			while (!stop && r_chain.size() > 2) {
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
	Triangle* t1 = new Triangle(r_chain[0], r_chain[1], tt->p[j]);
	Triangle* t2 = new Triangle(tt->p[j], l_chain[1], l_chain[0]);
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
	for (Triangle* dt : removed) {
		//print_triangle(dt);
		triangles.erase(dt);
		delete dt;
	}
	triangles.insert(t1);
	triangles.insert(t2);
	for (Triangle* nt : inserted)
		triangles.insert(nt);
	for (auto work : works)
		std::get<0>(work)->t[std::get<1>(work)] = std::get<2>(work);
	return true;
}
//TODO


Triangle* Instance::find_triangle(int q1, int q2) {
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

void Instance::print_triangle(Triangle* t) {
	std::cout << "Triangle: " << t << std::endl;
	std::cout << t->p[0] << ':' << pts[t->p[0]] << std::endl;
	std::cout << t->p[1] << ':' << pts[t->p[1]] << std::endl;
	std::cout << t->p[2] << ':' << pts[t->p[2]] << std::endl;
	std::cout << t->t[0] << std::endl;
	std::cout << t->t[1] << std::endl;
	std::cout << t->t[2] << std::endl;
}

void Instance::DrawResult(std::string s) {

	MyNum minx(this->pts[0].x);
	MyNum miny(this->pts[0].y);
	MyNum maxx(this->pts[0].x);
	MyNum maxy(this->pts[0].y);
	for (int i = 0; i < this->pts.size(); i++) {
		if (minx > MyNum(this->pts[i].x)) minx = MyNum(this->pts[i].x);
		if (miny > MyNum(this->pts[i].y)) miny = MyNum(this->pts[i].y);
		if (maxx < MyNum(this->pts[i].x)) maxx = MyNum(this->pts[i].x);
		if (maxy < MyNum(this->pts[i].y)) maxy = MyNum(this->pts[i].y);
	}
	long long int width = (long long int)(maxx - minx).toDouble();
	long long int height = (long long int)(maxy - miny).toDouble();
	float rad = 1000. / width;
	width = (int)width * rad + 40;
	height = (int)height * rad + 40;
	int minw = 20 - (int)minx.toDouble() * rad;
	int minh = height + (int)miny.toDouble() * rad - 20;
	//cout<<"miny: "<<miny<<" maxy:" <<maxy<< " minh: "<<minh<<endl;


	cv::Mat img(height, width, CV_8UC3, cv::Scalar(255, 255, 255));
	std::random_device rd;
	std::mt19937 gen(rd());
	std::uniform_int_distribution<int> dis(220, 255);
	for (Triangle* t : this->triangles) {
		cv::Point triangle_pt[1][3];
		triangle_pt[0][0] = cv::Point(minw + (int)this->pts[t->p[0]].x.toDouble() * rad, minh - (int)this->pts[t->p[0]].y.toDouble() * rad);
		triangle_pt[0][1] = cv::Point(minw + (int)this->pts[t->p[1]].x.toDouble() * rad, minh - (int)this->pts[t->p[1]].y.toDouble() * rad);
		triangle_pt[0][2] = cv::Point(minw + (int)this->pts[t->p[2]].x.toDouble() * rad, minh - (int)this->pts[t->p[2]].y.toDouble() * rad);
		const cv::Point* ppt[1] = { triangle_pt[0] };
		int npt[] = { 3 };

		fillPoly(img, ppt, npt, 1, cv::Scalar(dis(gen), dis(gen), dis(gen)), 8);
	}

	std::set<std::pair<int, int>> const_edges;
	std::set<std::pair<int, int>> int_edges;
	for (std::pair<int, int> e : this->constraints) {
		const_edges.insert(sorted_pair(e.first, e.second));
		cv::line(img, cv::Point(minw + (int)this->pts[e.first].x.toDouble() * rad, minh - (int)this->pts[e.first].y.toDouble() * rad), cv::Point(minw + (int)this->pts[e.second].x.toDouble() * rad, minh - (int)this->pts[e.second].y.toDouble() * rad), cv::Scalar(0, 0, 255), 2);
	}
	cout << this->boundary.size() << endl;
	for (int i = 1; i < this->boundary.size(); i++) {
		const_edges.insert(sorted_pair(this->boundary[i - 1], this->boundary[i]));
		cv::line(img, cv::Point(minw + (int)this->pts[this->boundary[i - 1]].x.toDouble() * rad, minh - (int)this->pts[this->boundary[i - 1]].y.toDouble() * rad), cv::Point(minw + (int)this->pts[this->boundary[i]].x.toDouble() * rad, minh - (int)this->pts[this->boundary[i]].y.toDouble() * rad), cv::Scalar(255, 0, 0), 2);
	}
	const_edges.insert(sorted_pair(this->boundary[0], this->boundary[this->boundary.size() - 1]));
	//cout<<"const edges"<<endl;
	for (std::pair<int, int> e : const_edges)
		//cout<<e.first<<" "<<e.second<<endl;
		cv::line(img, cv::Point(minw + (int)this->pts[this->boundary[0]].x.toDouble() * rad, minh - (int)this->pts[this->boundary[0]].y.toDouble() * rad), cv::Point(minw + (int)this->pts[this->boundary[this->boundary.size() - 1]].x.toDouble() * rad, minh - (int)this->pts[this->boundary[this->boundary.size() - 1]].y.toDouble() * rad), cv::Scalar(255, 0, 0), 2);
	//cout<<"new edges"<<endl;
	for (Triangle* t : this->triangles) {
		std::pair<int, int> e1 = sorted_pair(t->p[0], t->p[1]);
		std::pair<int, int> e2 = sorted_pair(t->p[1], t->p[2]);
		std::pair<int, int> e3 = sorted_pair(t->p[0], t->p[2]);
		auto cend = const_edges.end();
		auto iend = int_edges.end();
		if (const_edges.find(e1) == cend && int_edges.find(e1) == iend) {
			int_edges.insert(e1);
			cv::line(img, cv::Point(minw + (int)this->pts[e1.first].x.toDouble() * rad, minh - (int)this->pts[e1.first].y.toDouble() * rad), cv::Point(minw + (int)this->pts[e1.second].x.toDouble() * rad, minh - (int)this->pts[e1.second].y.toDouble() * rad), cv::Scalar(0, 0, 0), 2);
		}
		if (const_edges.find(e2) == cend && int_edges.find(e2) == iend) {
			int_edges.insert(e2);
			cv::line(img, cv::Point(minw + (int)this->pts[e2.first].x.toDouble() * rad, minh - (int)this->pts[e2.first].y.toDouble() * rad), cv::Point(minw + (int)this->pts[e2.second].x.toDouble() * rad, minh - (int)this->pts[e2.second].y.toDouble() * rad), cv::Scalar(0, 0, 0), 2);
		}
		if (const_edges.find(e3) == cend && int_edges.find(e3) == iend) {
			int_edges.insert(e3);
			cv::line(img, cv::Point(minw + (int)this->pts[e3.first].x.toDouble() * rad, minh - (int)this->pts[e3.first].y.toDouble() * rad), cv::Point(minw + (int)this->pts[e3.second].x.toDouble() * rad, minh - (int)this->pts[e3.second].y.toDouble() * rad), cv::Scalar(0, 0, 0), 2);
		}
	}
	for (int i = 0; i < this->pts.size(); i++) {
		if (i < this->fp_ind) cv::circle(img, cv::Point(minw + (int)this->pts[i].x.toDouble() * rad, minh - (int)this->pts[i].y.toDouble() * rad), 5, cv::Scalar(0, 0, 0), cv::FILLED);
		else cv::circle(img, cv::Point(minw + (int)this->pts[i].x.toDouble() * rad, minh - (int)this->pts[i].y.toDouble() * rad), 5, cv::Scalar(255, 0, 0), cv::FILLED);
	}

	cv::imwrite("solutions/" + this->instance_name + "_" + s + ".solution.png", img);
}