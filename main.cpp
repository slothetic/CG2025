#include "MyNum.h"
#include "data.h"
#include <iostream>

int main(int argc, char** argv){
	Data dt;
	std::cout << "input instance: " << argv[1] << std::endl;
	dt.input = argv[1];
	dt.ReadData();
	std::cout << dt.inst->fp_ind << std::endl;
	dt.inst->triangulate();
	std::cout << dt.inst->triangles.size() << std::endl;
	dt.WriteData();
	dt.DrawResult();
	dt.inst->minmax_triangulate();
	dt.inst->DrawResult("minmax");
	dt.WriteData();
	return 0;
}
