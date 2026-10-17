import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
RED,BLUE="#c0392b","#1f5fa8"
def col(frag,c): return f'<g stroke="{c}">'+frag.replace('fill="#000"',f'fill="{c}"')+'</g>\n'
def ctext(c,*a,**k): return text(*a,**k).replace('fill="#000"',f'fill="{c}"')
# per-phase values
V=219.39; X=0.1; I=151.93; phi=math.radians(36.87)
jx_re=X*I*math.sin(phi); jx_im=X*I*math.cos(phi)      # 9.12, 12.15
E_re=V+jx_re; E_im=jx_im
W,H=720,400; s=header(W,H)
k=2.0; ox,oy=40,250                                    # 2 px per volt
vx=ox+k*V; ex,ey=ox+k*E_re, oy-k*E_im
s+=col(arrow(ox,oy,vx,oy),BLUE)                                  # V_phi
s+=col(arrow(ox,oy,ex,ey),BLUE)                                  # E_f
s+=col(arrow(vx,oy,ex,ey),BLUE)                                  # jXsIa
ki=0.8                                                 # current scale (px per A)
s+=col(arrow(ox,oy,ox+ki*I*math.cos(phi),oy+ki*I*math.sin(phi)),RED)
# angle arcs
s+=f'<path d="M{ox+50} {oy} A50 50 0 0 1 {ox+50*math.cos(phi):.1f} {oy+50*math.sin(phi):.1f}"/>\n'
d=math.atan2(E_im,E_re); R=300
s+=f'<path d="M{ox+R} {oy} A{R} {R} 0 0 0 {ox+R*math.cos(d):.1f} {oy-R*math.sin(d):.1f}"/>\n'
s+=line(ox+R+1,oy-8,ox+R+12,214)                      # leader to delta label
s+=dot(ox,oy)
# zoom circle + leader
zc=(vx+9,oy-12)
s+=f'<circle cx="{zc[0]:.1f}" cy="{zc[1]:.1f}" r="22" stroke-dasharray="4 4" stroke-width="1"/>\n'
s+=f'<path d="M{zc[0]+22:.1f} {zc[1]:.1f} L540 180" stroke-dasharray="4 4" stroke-width="1"/>\n'
# inset (8 px per volt = 4x main)
s+=f'<rect x="540" y="56" width="172" height="334" stroke-dasharray="6 4" stroke-width="1"/>\n'
m=8.0; px,py=578,330
qx,qy=px+m*jx_re,py-m*jx_im
s+=col(arrow(550,py,px,py),BLUE)                                 # V_phi tip
s+=col(arrow(px,py,qx,qy),BLUE)                                  # jXsIa
s+=col(arrow(qx-110,qy+110*math.tan(d),qx,qy),BLUE)              # E_f tip (slope delta)
s+=f'<path d="M{px} {py} L{qx:.1f} {py}" stroke-dasharray="5 4" stroke-width="1"/>\n'
s+=f'<path d="M{qx:.1f} {py} L{qx:.1f} {qy:.1f}" stroke-dasharray="5 4" stroke-width="1"/>\n'
a=math.radians(53.13)
s+=f'<path d="M{px+26} {py} A26 26 0 0 0 {px+26*math.cos(a):.1f} {py-26*math.sin(a):.1f}"/>\n'
s+=end_group()
s+=text(30,32,[("t","比例：電壓 1 V = 2 px（"),("v","V"),("vsub","φ"),("t","、"),("v","E"),("vsub","f"),("t","、"),("v","jX"),("vsub","s"),("n","\u200a"),("v","I"),("vsub","a"),("t"," 同一比例）；"),("v","I"),("vsub","a"),("t"," 另用電流比例")])
s+=text(ox-8,oy+6,[("v","O")],anchor="end")
s+=ctext(BLUE,250,276,[("v","V"),("vsub","φ"),("n"," = 219.39∠0° V")])
s+=ctext(BLUE,110,222,[("v","E"),("vsub","f"),("n"," = 228.83∠3.04° V")])
s+=text(ox+R+14,210,[("v","δ"),("n"," = 3.04°")])
s+=text(98,278,[("v","φ"),("n"," = 36.87°")])
s+=ctext(RED,150,372,[("v","I"),("vsub","a"),("n"," = 151.93∠−36.87° A")])
s+=text(552,80,[("t","尖端放大 4 倍")])
s+=text(552,104,[("v","jX"),("vsub","s"),("n","\u200a"),("v","I"),("vsub","a"),("n"," =")])
s+=text(552,124,[("n","15.19∠53.13° V")])
s+=text(qx,qy-28,[("v","E"),("vsub","f"),("t"," 尖端")],anchor="middle")
s+=text(552,py-22,[("v","V"),("vsub","φ"),("t"," 端")])
s+=text(px+30,py-8,[("n","53.13°")])
s+=text((px+qx)/2,py+22,[("n","9.12 V")],anchor="middle")
s+=text(qx+8,(py+qy)/2,[("n","12.15")])
s+=text(qx+8,(py+qy)/2+18,[("n","V")])
s+=footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-107-04-4-phasor.svg'),'w').write(s)
print(len(s))
