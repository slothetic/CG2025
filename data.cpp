#include "feasible.h"

//Point::Point(){x=0;y=0;}
//Point::Point(int _x, int _y){x=_x; y=_y;}

bool is_left(cv::Point p1, cv::Point p2, cv::Point p3){
	return (p2.x-p1.x)*(p3.y-p1.y)-(p2.y-p1.y)*(p3.x-p1.x)>0;
}

Polygon::Polygon(){vers.assign(1, cv::Point());x_loc=0;y_loc=0;}

Polygon::Polygon(vector<cv::Point> _vers){
	vers = _vers;
	x_loc=0;
	y_loc=0;
	for (int i=0;i<vers.size();i++){
		x_vers.push_back(vers[i].x);
		y_vers.push_back(vers[i].y);
	}
	use=false;
}

Polygon::Polygon(vector<int> _x_vers, vector<int> _y_vers){
	x_vers = _x_vers;
	y_vers = _y_vers;
	x_loc=0;
	y_loc=0;
	for (int i=0;i<x_vers.size();i++){
		vers.push_back(cv::Point(x_vers[i], y_vers[i]));
	}
	use=false;
}

Polygon Polygon::make_convex(){
	vector<cv::Point> vers;
	int max_x = 0;
	int max_x_ind = 0;
	for (int i=0;i<this->vers.size();i++){
		if (this->x_vers[i]>max_x){
			max_x = this->x_vers[i];
			max_x_ind = i;
		}
	}
	vers.push_back(this->vers[max_x_ind]);
	for (int i=0;i<this->vers.size();i++){
		int ind = (i+max_x_ind+1)%(this->vers.size());
		if (vers.size()==1){
			vers.push_back(this->vers[ind]);
		}
		else{
			while(is_left(vers[-2], vers[-1], this->vers[ind])) {
				vers.pop_back();
				if (vers.size()==1) break;
			}
			vers.push_back(this->vers[ind]);
		}
	}
	vers.pop_back();
	Polygon newP = Polygon(vers);
	return newP;
}

bool Polygon::intersect(Polygon P){
	return true;	
}

void Feasible::ReadData(){
	cout << "--------------------ReadData--------------------" << endl;
	x_max= 0;
	y_max =0;
	Json::Value root;
	Json::Reader reader;
	string path=input;
	ifstream json(path, ifstream::binary);
	reader.parse(json, root);

	instance_name =  root["instance_name"].asString();
	num_items = root["num_items"].asInt();
	Json::Value _container = root["container"];
	vector<cv::Point> c_vers;
	for (int i=0;i<_container["x"].size();i++){
		c_vers.push_back(cv::Point(_container["x"][i].asInt(), _container["y"][i].asInt()));
		x_max = max(x_max, _container["x"][i].asInt());
		y_max = max(y_max, _container["y"][i].asInt());
		x_min = min(x_min, _container["x"][i].asInt());
		y_min = min(y_min, _container["y"][i].asInt());
		
	}

	container = Polygon(c_vers);
	container.cont = true;
	int ind = 0;
	for (auto& item:root["items"]){
		int _value = item["vlaue"].asInt();
		vector<cv::Point> i_vers;

	  for (int i=0;i<_container["x"].size();i++){
		  c_vers.push_back(cv::Point(_container["x"][i].asInt(), _container["y"][i].asInt()));
	  }
		Polygon P = Polygon(c_vers);
		P.value = _value;
		P.index = ind;
		ind++;
		for (int j=0;j<item["quantity"].asInt();j++){
			items.push_back(P);
		}
		
	}

	type = root["type"].asString();
	cout << "-number of items: " << items.size() << endl;
}

void Feasible::WriteResult(){
	cout << "--------------------WriteResult--------------------" << endl;

	int num_item=0;
	int value_item=0;
	vector<int> item_indices;
	vector<int> x_trans;
	vector<int> y_trans;
	for (auto& item:items){
		if (item.use) {
			num_item++;
			value_item=value_item+item.value;
			item_indices.push_back(item.index);
			x_trans.push_back(item.x_loc);
			y_trans.push_back(item.y_loc);
		}
	}
	string filename;
	filename = instance_name+"_result.json";
	ofstream solution(filename);

	solution<<"{\"type\": \"cgshop2024_solution\",\n";
	solution<<"\"instance_name\": \""<< instance_name <<"\",\n";
	solution<<"\"num_included_items\": \""<< num_item <<"\",\n";
	/*
	solution<<"\"total_value\": \""<< value_item <<"\",\n";
	solution<<"\"container\": {\"x\": [";
	for (int i=0;i<container.vers.size();i++){
		if (i<container.vers.size()-1){
			solution<<container.x_vers[i]<<", ";
		}
		else{
			solution<<container.x_vers[i]<<"],\n";
		}
	}
	solution<<"\"y\": [";
	for (int i=0;i<container.vers.size();i++){
		if (i<container.vers.size()-1){
			solution<<container.y_vers[i]<<", ";
		}
		else{
			solution<<container.y_vers[i]<<"]},\n";
		}

	}
	solution<<"\"items\": [";
	solution<<"]\n";
	*/

	solution<<"\"item_indices\": "<< "[";
	for (int i=0;i<item_indices.size();i++){
		if (i<item_indices.size()-1){
			solution<<item_indices[i]<<", ";
		}
		else{
			solution<<item_indices[i];
		}
	}
	solution<<"],\n";

	solution<<"\"x_trans\": "<< "[";
	for (int i=0;i<x_trans.size();i++){
		if (i<x_trans.size()-1){
			solution<<x_trans[i]<<", ";
		}
		else{
			solution<<x_trans[i];
		}
	}
	solution<<"],\n";
	solution<<"\"y_trans\": "<< "[";
	for (int i=0;i<y_trans.size();i++){
		if (i<y_trans.size()-1){
			solution<<y_trans[i]<<", ";
		}
		else{
			solution<<y_trans[i];
		}
	}
	solution<<"],\n";
  solution<<"}\n";
	solution.close();
}


void Feasible::DrawResult(){
	cout << "--------------------DrawResult--------------------" << endl;
	float xy_max = min(x_max, y_max);
	float ratio = 400./xy_max;
	cv::Mat img(int(ratio*x_max*1.08), int(ratio*y_max*1.08), CV_8UC3, cv::Scalar(255, 255, 255));
	vector<cv::Point> vers;
	for (auto p:container.vers){
		vers.push_back(cv::Point(int(p.x*ratio), int(p.y*ratio)));
	}
	cv::polylines(img, vers, true, cv::Scalar(255, 0, 255), 2);

	cv::imwrite("check.bmp", img, vector<int>());
}


