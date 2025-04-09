import sys
from data import Data
if __name__=="__main__":
    argument = sys.argv
    if len(argument)>=2:
        inp = argument[1]
    dt = Data(inp)
    # dt.triangulate()
    # dt.delaunay_triangulate()
    dt.WriteData(self_update=True)
    print(inp)