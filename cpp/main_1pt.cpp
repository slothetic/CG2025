#include "MyNum.h"
#include "data.h"
#include <iostream>

int main(int argc, char** argv){
	Data dt;
	std::cout << "input instance: " << argv[1] << std::endl;
	dt.input = argv[1];
	dt.ReadData();
	std::cout << dt.inst->fp_ind << std::endl;
	dt.inst->pts.push_back(Point(MyNum(500000),MyNum(500000)));
	dt.inst->triangulate();
	std::cout << dt.inst->triangles.size() << std::endl;
	dt.WriteData();
	dt.inst->DrawResult("1stpt");
	return 0;
}
