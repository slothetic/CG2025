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
	int cnt = 0;
	while(true) {
		cnt++;
		char ans;
		std::cout << "Try a step?(y/n):";
		std::cin >> ans;
		if (ans == 'n') break;
		else if (ans == 'y') {
			dt.inst->step();
			dt.inst->DrawResult(std::to_string(cnt));
		}
	}
	for (int asdf : dt.inst->boundary) std::cout << asdf << ' ';
	std::cout << std::endl;
	dt.WriteData();
	dt.inst->DrawResult("nonobt");
	return 0;
}
