import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
W,H=680,360; s=header(W,H)
s+=busbar(115,205,100)+busbar(470,560,100)+busbar(300,380,262)
s+=coil(205,100,470,100,turns=6)                      # line 1-2
s+=coil(185,100,315,262,turns=4)                      # line 1-3
s+=coil(495,100,365,262,turns=4)                      # line 3-2
# gen branches
s+=coil(150,100,150,196,turns=4)+line(150,196,150,214)+ac_source(150,228)+line(150,242,150,310)
s+=coil(535,100,535,196,turns=4)+line(535,196,535,214)+ac_source(535,228)+line(535,242,535,310)
# fault branch Zf at bus 1
s+=line(115,100,70,100)+coil(70,100,70,210,turns=4)+line(70,210,70,310)
s+=line(40,310,600,310)
s+=arrow(88,228,88,268)
s+=end_group()
s+=text(160,88,[("n","Bus 1")])
s+=text(515,88,[("n","Bus 2")],anchor="middle")
s+=text(340,288,[("n","Bus 3")],anchor="middle")
s+=text(338,82,[("v","j"),("n","0.8")],anchor="middle")
s+=text(270,196,[("v","j"),("n","0.4")])
s+=text(410,196,[("v","j"),("n","0.4")],anchor="end")
s+=text(160,152,[("v","j"),("n","0.2")])
s+=text(160,172,[("t","（"),("v","G"),("sub","1"),("t","＋"),("v","T"),("sub","1"),("t","）")])
s+=text(523,152,[("v","j"),("n","0.4")],anchor="end")
s+=text(523,172,[("t","（"),("v","G"),("sub","2"),("t","＋"),("v","T"),("sub","2"),("t","）")],anchor="end")
s+=text(56,150,[("v","Z"),("vsub","f")],anchor="end")
s+=text(56,170,[("v","j"),("n","0.11")],anchor="end")
s+=text(96,254,[("v","I"),("vsub","f")])
s+=text(320,336,[("t","參考點（各發電機 EMF 短路接地）")],anchor="middle")
s+=footer()
open(__import__('pathlib').Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-106-05-2-positive-network.svg'),'w').write(s)
print(len(s))
