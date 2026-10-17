import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
RED,BLUE="#c0392b","#1f5fa8"
def col(frag,c): return f'<g stroke="{c}">'+frag.replace('fill="#000"',f'fill="{c}"')+'</g>\n'
def ctext(c,*a,**k): return text(*a,**k).replace('fill="#000"',f'fill="{c}"')
W,H=700,290; s=header(W,H); y=96
s+=f'<path d="M40 {y-34} L40 {y+34}" stroke-width="5"/>\n'          # infinite bus
s+=line(40,y,70,y)+coil(70,y,190,y,turns=5)+line(190,y,304,y)      # source S
s+=f'<circle cx="320" cy="{y}" r="16"/>\n<circle cx="342" cy="{y}" r="16"/>\n'  # two-winding transformer
s+=line(358,y,470,y)+coil(470,y,590,y,turns=5)+line(590,y,640,y)   # line L
for x in (240,430,640):
    s+=dot(x,y)+col(arrow(x,y+8,x,y+48),RED)
s+=end_group()
s+=text(40,42,[("t","∞ 母線")],anchor="middle")
for x,name,val in ((130,[("t","電源 "),("v","S")],"200 MVA"),(331,[("t","變壓器 "),("v","T")],"10 MVA"),(530,[("t","線路 "),("v","L")],"2 MVA")):
    s+=text(x,48,name,anchor="middle")+text(x,70,[("n",val)],anchor="middle")
s+=text(331,128,[("n","11.4/0.38 kV")],anchor="middle")
for x,i,mva,kv,ka in ((240,"1","200 MVA","11.4 kV","10.13 kA"),(430,"2","9.52 MVA","0.38 kV","14.47 kA"),(640,"3","1.65 MVA","0.38 kV","2.51 kA")):
    s+=text(x,78,[("v","F"),("sub",i)],anchor="middle")
    s+=text(x,174,[("n",mva)],anchor="middle")+text(x,194,[("n",kv)],anchor="middle")+ctext(RED,x,214,[("n",ka)],anchor="middle")
s+=text(350,262,[("t","串聯合成："),("n","1/MVA"),("vsub","F"),("n"," = Σ 1/MVA"),("vsub","i"),("t","；"),("v","I"),("n"," = MVA"),("vsub","F"),("n"," / (√3 kV)")],anchor="middle")
s+=footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-112-06-3-mva-chain.svg'),'w').write(s)
print(len(s))
