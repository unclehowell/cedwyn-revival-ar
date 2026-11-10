
import sys, math, json, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from glb import Model
OUT=sys.argv[1]; os.makedirs(OUT, exist_ok=True)
S=json.load(open(os.path.join(os.path.dirname(__file__),'..','SITES.json')))
site={s['id']:s for s in S['sites']}
def meta(sid, extra=None):
    s=site[sid]; d={"site_id":sid,"name":s['name'],"lat":s['lat'],"lon":s['lon'],"axes":"metres; +x east, +y up, +z south; origin = the pin (lat,lon) at ground level",
       "period":s['period'],"confidence":s['confidence'],"label":"reconstruction — estimated where marked; see SITES.json known/estimated","estimated":s['estimated'],
       "evidence":[e['label']+(' '+e['url'] if e['url'] else '') for e in s['evidence']],"version":"0.1.0","by":"Sion's Tab agent"}
    if extra: d.update(extra)
    return d
sizes={}
# ---------------- ROUNDHOUSE ----------------
m=Model('roundhouse')
m.mat('daub',(0.66,0.56,0.42),0.95); m.mat('thatch',(0.52,0.42,0.25),1.0); m.mat('timber',(0.34,0.24,0.15),0.9); m.mat('door',(0.18,0.13,0.09),0.9)
R=5.0; m.ringwall('daub',0,0,R,1.6,0.35,seg=40,gap=(0,1.6*180/math.pi/R*1.0))   # doorway facing east (estimated)
m.cyl('thatch',0,0,R+1.0,5.4,y0=1.6,seg=40,top=False,r_top=0.0)
m.cyl('timber',0,0,0.18,7.0,seg=10)
for a in (-12,12): m.box('timber',R+0.7,math.tan(math.radians(a))*R*0.9,1.6,0.25,2.0,yaw=0)  # porch posts
m.box('door',R-0.05,0,0.1,1.3,1.5)
for i in range(64):  # palisade (estimated)
    a=2*math.pi*i/64
    if abs(((math.degrees(a)+180)%360)-180)<6: continue
    m.cyl('timber',22*math.cos(a),22*math.sin(a),0.14,2.2,seg=6)
sizes['roundhouse']=m.save(os.path.join(OUT,'roundhouse.glb'),meta('roundhouse',{"dims":"hut d 10 m, wall 1.6 m, apex 7 m, palisade r 22 m — all estimated"}))
# ---------------- VILLA ----------------
m=Model('villa')
m.mat('plaster',(0.90,0.86,0.76),0.8); m.mat('stone',(0.58,0.55,0.48),0.9); m.mat('tile',(0.68,0.33,0.2),0.7); m.mat('col',(0.86,0.83,0.76),0.6)
m.mat('court',(0.62,0.58,0.5),1.0); m.mat('water',(0.25,0.4,0.5),0.2)
TH=47.0; c,s=math.cos(math.radians(TH)),math.sin(math.radians(TH))
def UV(u,v): return (u*c-v*s, u*s+v*c)
def blk(u,v,w,d,eave,pitch,ridge='x'):
    x,z=UV(u,v)
    m.box('stone',x,z,w+0.2,d+0.2,0.5,yaw=TH)
    m.box('plaster',x,z,w,d,eave,y0=0.5,yaw=TH,top=False)
    m.gable('tile','plaster',x,z,w,d,eave+0.5,pitch,yaw=TH,ridge_along=ridge)
blk(0,0,45,7,3.0,28)                 # main range, traced length (Fig. 2)
blk(-19,-1.5,13,14,3.4,28,'z')       # NW room group (Fig. 2)
blk(19.5,1.5,14,15,3.4,28,'z')       # SE group incl. hypocaust room / bath suite (HER)
# portico on the courtyard (SW) side — estimated
for i in range(15):
    x,z=UV(-21+i*3.0,5.2); m.cyl('col',x,z,0.18,2.6,y0=0.3,seg=10)
x,z=UV(0,5.0); m.box('stone',x,z,45,3.2,0.3,yaw=TH); m.box('tile',x,z,45,3.4,0.15,y0=2.9,yaw=TH)
# courtyard + precinct wall (named in HER, plan estimated)
x,z=UV(0,18); m.box('court',x,z,44,24,0.05,yaw=TH)
for a,b in [((-22,6.6),(-22,30)),((22,6.6),(22,30)),((-22,30),(-2.2,30)),((2.2,30),(22,30))]:
    m.wall('stone',UV(*a),UV(*b),1.8,0.6)
x,z=UV(10,18); m.box('water',x,z,3,6,0.12,yaw=TH)  # pipe-fed tank (pipe trench in HER; tank estimated)
sizes['villa']=m.save(os.path.join(OUT,'villa.glb'),meta('villa',{"dims":"main range 45 m on bearing 137 deg (Fig. 2 traced); heights, roofs, portico, courtyard and wall line estimated"}))
# ---------------- MONASTERY ----------------
m=Model('monastery')
m.mat('timber',(0.36,0.25,0.15),0.9); m.mat('thatch',(0.52,0.42,0.25),1.0); m.mat('bank',(0.42,0.46,0.28),1.0); m.mat('stone',(0.6,0.58,0.53),0.85); m.mat('mark',(0.55,0.53,0.48),0.9)
cx,cz=13,31          # St Dochdwy's site relative to cemetery centre (OSM)
m.box('timber',cx,cz,12,6,3.2,top=False); m.gable('thatch','timber',cx,cz,12,6,3.2,50)
m.box('timber',cx+7.5,cz,3,4,2.6,top=False); m.gable('thatch','timber',cx+7.5,cz,3,4,2.6,50)   # chancel, estimated
# pillar cross (Coflein 301373: 2.97 m composite pillar, no head; ST1679073250)
px,pz=-7.8,42.4
m.box('stone',px,pz,0.9,0.9,0.5); m.box('stone',px,pz,0.45,0.4,1.25,y0=0.5); m.box('stone',px,pz,0.6,0.55,0.22,y0=1.75); m.box('stone',px,pz,0.4,0.35,1.0,y0=1.97)
# curvilinear enclosure (estimated)
m.ringwall('bank',6,16,45,1.4,2.2,seg=72,gap=(0,10))
# graves: Area II rows SW/NE west of centre; Area I curve (sample, not the excavated plan)
import random; random.seed(7)
for row in range(8):
    for k in range(9):
        u=-26+row*2.2; v=-14+k*2.0
        x=u*0.707-v*0.707; z=u*0.707+v*0.707
        m.box('mark',x-6,z+4,0.5,1.8,0.12,yaw=45)
for i in range(30):
    a=math.radians(200+i*4.5); r=18+random.uniform(-1,1)
    m.box('mark',6+r*math.cos(a),8+r*math.sin(a),0.5,1.8,0.12,yaw=math.degrees(a))
sizes['monastery']=m.save(os.path.join(OUT,'monastery.glb'),meta('monastery',{"dims":"church/oratory 12x6 m estimated at St Dochdwy's; pillar cross 2.97 m (Coflein 301373); enclosure r 45 m estimated; grave markers a sample"}))
# ---------------- TY MAWR ----------------
# v0.2.0 (5 Nov 2026): layout from tools/tymawr-layout.json — house and stable range face south, stable front level with the
# house front, the west barn runs north-south and faces west (the Executive's written corrections; reference paintings + aerial).
G=json.load(open(os.path.join(os.path.dirname(__file__),'tymawr-layout.json')))
m=Model('tymawr')
# issue #200 (3D model loop): stone colours are glTF linear factors of the paintings' honey-grey rubble and cream dressed limestone (were near-white grey)
# realism pass (3D model loop, 5 Nov 2026, the Executive's 10:16 direction): wall/roof textures are sampled from the 1988 Cadw survey
# photographs of the house and barn (tools/tex/*.jpg, 256 px, box-projected); factors become a tint (1,1,1 = the photo's colour).
TX=os.path.join(os.path.dirname(__file__),'tex')
m.mat('limewash',(1,1,1),0.9,tex=os.path.join(TX,'limewash.jpg'),tile=2.2); m.mat('slate',(1,1,1),0.6,tex=os.path.join(TX,'slate_house.jpg'),tile=2.4); m.mat('pantile',(1,1,1),0.75,tex=os.path.join(TX,'pantile.jpg'),tile=2.0)
m.mat('rubble',(1,1,1),0.95,tex=os.path.join(TX,'rubble_house.jpg'),tile=1.6); m.mat('dressed',(1,1,1),0.9,tex=os.path.join(TX,'rubble_barn.jpg'),tile=2.0)
m.mat('slate_barn',(1,1,1),0.6,tex=os.path.join(TX,'slate_barn.jpg'),tile=2.4); m.mat('ridge',(0.26,0.07,0.04),0.7); m.mat('frame',(0.85,0.84,0.80),0.6); m.mat('timber',(0.20,0.14,0.09),0.85)
m.mat('porch_tbr',(0.018,0.019,0.021),0.8); m.mat('porch_roof',(0.07,0.048,0.03),0.75)   # run 16 (#470): porch timber and roof sampled from the 1988 farmhouse photograph (sRGB 0.05/0.055/0.07 and 0.29/0.24/0.18; linear factors)
m.mat('brick',(0.20,0.06,0.035),0.85); m.mat('green',(0.16,0.33,0.2),0.6); m.mat('gravel',(0.33,0.30,0.25),1.0); m.mat('glass',(0.04,0.045,0.05),0.35,0.0)
m.mat('olive',(0.05,0.065,0.038),0.7); m.mat('frame_dk',(0.04,0.05,0.03),0.7); m.mat('bayshade',(0.17,0.155,0.13),0.95)   # run 12: stable doors/frames sampled from the paintings (sRGB 0.33/0.35/0.24 in the barn-and-stables painting -> linear); shaded limewash for the open bay
m.mat('dark',(0.08,0.08,0.08),0.9); m.mat('boards',(0.42,0.40,0.35),0.9); m.mat('gate',(0.10,0.11,0.10),0.7); m.mat('pane',(0.55,0.64,0.66),0.1,0.0,0.62); m.mat('bark',(0.30,0.22,0.15),0.95); m.mat('leaf',(0.075,0.10,0.04),1.0)   # run 4 (#201): leaf colour sampled from the house-and-gate painting's tree (sRGB median 0.28/0.31/0.20 -> linear), was (0.24,0.36,0.18) and read mint; run 7 (#202): pane greyer and less see-through (was (0.75,0.85,0.85) alpha 0.45)
WM={'limewash':'limewash','rubble stone':'rubble','dressed stone':'dressed'}; RM={'slate':'slate','red pantile':'pantile'}
for b in G['buildings']:
    if b['id']=='church': continue
    wm=WM.get(b.get('walls'),'limewash'); rm=RM.get(b.get('roof'),'slate')
    if b['id'].startswith('stone_barn'): rm='slate_barn'   # the 1988 barn photograph: paler, weathered slate
    if 'len_ew' in b: w,d,ridge=b['len_ew'],b['dep_ns'],'x'
    else: w,d,ridge=b['dep_ew'],b['len_ns'],'z'
    m.box(wm,b['x'],b['z'],w,d,b['eave'],top=False)
    ry=m.gable(rm,wm,b['x'],b['z'],w,d,b['eave'],b['pitch'],ridge_along=ridge,hip0=b.get('hip_west_pitch'),hip1=b.get('hip_east_pitch'))
    for ch in b.get('chimneys',[]):   # 'x' (offset from the building centre), 'w', 'd', 'h' (height above the ridge): measured from the 1988 photograph (3D model loop run 3)
        at=ch.get('at') or ('left' if ch.get('x',0)<1 else 'right')
        cxx={'left':b['x']-w/2+0.5,'centre':b['x'],'right':b['x']+w/2-0.5}[at]
        if 'x' in ch: cxx=b['x']+ch['x']
        h0=ry-1.2 if ('x' in ch or at=='centre') else b['eave']
        cw,cd,chh=ch.get('w',0.9),ch.get('d',1.0),ch.get('h',1.0)
        m.box('brick' if 'brick' in ch['mat'] else 'rubble',cxx,b['z'],cw,cd,ry-h0+chh,y0=h0)
        cpp,cph=ch.get('cap_proud',0.06),ch.get('cap_h',0.15); m.box('brick' if 'brick' in ch['mat'] else 'rubble',cxx,b['z'],cw+2*cpp,cd+2*cpp,cph,y0=ry+chh-0.1-cph)   # projecting cap course (run 17, #469: per-stack 'cap_proud'/'cap_h'; defaults = the earlier 6 cm / 0.15 m course)
        if ch.get('pot'): m.cyl('rubble',cxx,b['z'],ch['pot'],0.45,y0=ry+chh-0.1,seg=8)   # run 16 (#469): buff chimney pot (1988 farmhouse photograph, west stack)
    if 'chimney' in b: m.box('rubble',b['x'],b['z']-d/2+0.6,1.0,0.9,ry-b['eave']+1.0,y0=b['eave'])
    if b.get('ridge_tiles'):   # red clay ridge tiles (1988 photographs of house and barn)
        if ridge=='x' and b.get('hip_west_pitch'):   # hipped west end: ridge tiles from the hip apex east, plus the two hip lines
            xr=b['x']+m.hip_ridge; xe=b['x']+w/2+0.3; m.box('ridge',(xr+xe)/2,b['z'],xe-xr,0.32,0.2,y0=ry-0.08)
            for sz in (1,-1):
                a=[b['x']-w/2,b['eave'],b['z']+sz*d/2]; c=[xr,ry,b['z']]
                mid=[(a[0]+c[0])/2,(a[1]+c[1])/2,(a[2]+c[2])/2]; ln=math.dist(a,c)
                hor=math.hypot(c[0]-a[0],c[2]-a[2]); yaw=math.degrees(math.atan2(c[2]-a[2],c[0]-a[0]))
                if b.get('hip_tiles')=='strip':   # run 17: one smooth capped strip along each hip line (the stepped boxes read as a red staircase at housephoto); 'hip_mat' picks its material
                    A_,C_=np.array(a,float),np.array(c,float); u_=(C_-A_)/np.linalg.norm(C_-A_); l_=np.cross(u_,[0,1,0]); l_=l_/np.linalg.norm(l_)*0.16; up_=np.array([0,0.07,0])
                    def _q(p0,p1,p2,p3,want):
                        nn=np.cross(p1-p0,p2-p0)
                        if np.dot(nn,want)<0: p1,p3=p3,p1
                        m.quad(b.get('hip_mat','ridge'),p0.tolist(),p1.tolist(),p2.tolist(),p3.tolist())
                    _q(A_-l_+up_,C_-l_+up_,C_+l_+up_,A_+l_+up_,np.array([0,1.,0]))
                    for sg in (1,-1): _q(A_+sg*l_+up_,C_+sg*l_+up_,C_+sg*l_-up_*1.6,A_+sg*l_-up_*1.6,sg*l_)
                    continue
                n=max(2,int(ln/0.5))
                for k in range(n):   # hip tiles as short stepped pieces along the hip line
                    t=(k+0.5)/n; m.box('ridge',a[0]+(c[0]-a[0])*t,a[2]+(c[2]-a[2])*t,ln/n+0.05,0.3,0.16,y0=a[1]+(c[1]-a[1])*t-0.06,yaw=-yaw)
        elif ridge=='x': m.box('ridge',b['x'],b['z'],w+0.6,0.32,0.2,y0=ry-0.08)
        else: m.box('ridge',b['x'],b['z'],0.32,d+0.6,0.2,y0=ry-0.08)
    if b.get('gable_rubble_east'):   # 1988 photograph: the east gable is bare rubble, not limewashed
        xe=b['x']+w/2+0.03; m.box('rubble',xe,b['z'],0.04,d,b['eave'])
        m.tri('rubble',[[xe+0.02,b['eave'],b['z']+d/2],[xe+0.02,b['eave'],b['z']-d/2],[xe+0.02,ry,b['z']]])
    if b.get('downpipe_x') is not None:
        m.cyl('dark',b['x']+b['downpipe_x'],b['z']+d/2+0.12,0.06,b['eave'],seg=8)
        m.box('dark',b['x'],b['z']+d/2+0.15,w,0.16,0.12,y0=b['eave']-0.12)
    if 'porch' in b and b['porch'].get('open'):   # 1988 photograph: open timber porch, slate gable, door behind
        p=b['porch']; px=b['x']+p['x']; pz=b['z']+d/2+p['d']/2
        pt,pr=('porch_tbr','porch_roof') if p.get('dark') else ('timber','slate')   # run 16 (#470): 1988 photograph: dark-stained timber frame and gable, darker weathered roof than the main slate
        for sx in (-p['w']/2+0.1,p['w']/2-0.1): m.box(pt,px+sx,pz+p['d']/2-0.1,0.14,0.14,2.3)
        m.box(pt,px,pz+p['d']/2-0.1,p['w'],0.16,0.18,y0=2.25)
        m.gable(pr,pt,px,pz,p['w'],p['d'],2.4,40,ridge_along='z',over=0.15)
        m.box('green',px,b['z']+d/2+0.02,0.95,0.05,2.0)
    elif 'porch' in b:
        p=b['porch']; pz=b['z']+d/2+p['d']/2
        m.box(wm,b['x']+p['x'],pz,p['w'],p['d'],2.4,top=False); m.gable(rm,wm,b['x']+p['x'],pz,p['w'],p['d'],2.4,40,ridge_along='z')
        m.box('green',b['x']+p['x'],pz+p['d']/2+0.01,1.0,0.05,2.0)
    if b['id']=='house':   # windows: positions read from the 1988 photograph (house front 11 m); white frames, dark panes
        for win in b.get('windows',[(-3.6,1.2),(-1.2,1.2),(3.4,1.2),(-3.6,3.4),(-1.2,3.4),(3.4,3.4)]):
            wx,wy=win[0],win[1]; gw,gh=(win[2],win[3]) if len(win)>=4 else (0.85,1.05)   # [x, sill, glass w, glass h]: sizes measured per window (run 3)
            m.box('frame',b['x']+wx,b['z']+d/2+0.02,gw+0.2,0.05,gh+0.22,y0=wy-0.05)
            m.box('glass',b['x']+wx,b['z']+d/2+0.05,gw,0.04,gh,y0=wy+0.08)
            m.box('frame',b['x']+wx,b['z']+d/2+0.08,0.06,0.03,gh,y0=wy+0.08); m.box('frame',b['x']+wx,b['z']+d/2+0.08,gw,0.03,0.05,y0=wy+0.08+gh/2)
            if len(win)>=5 and win[4]=='shutter': m.box('dark',b['x']+wx+gw/2+0.2,b['z']+d/2+0.04,0.35,0.04,gh,y0=wy+0.08)
    for rl in b.get('rooflights',[]):   # run 13: glazed roof light lying on the south slope (1988 farmhouse photograph shows one in the pantile range near the house)
        if ridge!='x': continue
        pit=math.radians(b['pitch']); S=d/2+0.3; e=b['eave']-0.3*math.tan(pit); t0,t1=rl.get('t',0.35)-rl.get('l',0.8)/2/(S/math.cos(pit)),rl.get('t',0.35)+rl.get('l',0.8)/2/(S/math.cos(pit))
        nz,ny=math.sin(pit)*0.04,math.cos(pit)*0.04; x0,x1=b['x']+rl['x']-rl.get('w',0.6)/2,b['x']+rl['x']+rl.get('w',0.6)/2
        P=lambda x,t:[x,e+(ry-e)*t+ny,b['z']+S*(1-t)+nz]
        m.quad('frame_dk',P(x0-0.06,t0-0.03),P(x1+0.06,t0-0.03),P(x1+0.06,t1+0.03),P(x0-0.06,t1+0.03))
        m.quad('glass',[*P(x0,t0)[:1],P(x0,t0)[1]+0.01,P(x0,t0)[2]],[*P(x1,t0)[:1],P(x1,t0)[1]+0.01,P(x1,t0)[2]],[*P(x1,t1)[:1],P(x1,t1)[1]+0.01,P(x1,t1)[2]],[*P(x0,t1)[:1],P(x0,t1)[1]+0.01,P(x0,t1)[2]])
    if 'front' in b:   # run 13: any building with a 'front' list (stable range, pantile range); run 12 (3D model loop): south front read from the stable-range paintings AR-0024/AR-0004 — dark green boarded doors and window frames, small windows, an open bay with a door at its back
        zf=b['z']+d/2
        for o in b['front']:
            ox=b['x']+o['x']; k=o['k']
            if k=='door':
                m.box('olive',ox,zf+0.02,o.get('w',1.0),0.06,o.get('h',2.0)); m.box('frame_dk',ox,zf+0.055,o.get('w',1.0),0.02,0.06,y0=1.05)   # boarded door with a mid rail
            elif k=='window':
                ww,wh,sill=o.get('w',0.75),o.get('h',0.75),o.get('sill',1.1)
                m.box('olive',ox,zf+0.02,ww+0.16,0.05,wh+0.16,y0=sill-0.08); m.box('glass',ox,zf+0.05,ww,0.04,wh,y0=sill)
                m.box('olive',ox,zf+0.075,0.05,0.02,wh,y0=sill); m.box('olive',ox,zf+0.075,ww,0.02,0.05,y0=sill+wh/2-0.025); m.box('frame',ox,zf+0.04,ww+0.3,0.08,0.06,y0=sill-0.12)   # glazing bar, pale sill
            elif k=='bay':   # open-fronted bay: shaded back wall, floor, inner door (drawn on the face; the camera looks into it)
                bw,bh=o.get('w',3.2),o.get('h',2.35)
                m.box('bayshade',ox,zf+0.015,bw,0.05,bh); m.box('timber',ox,zf+0.07,bw+0.3,0.1,0.22,y0=bh); m.box('olive',ox+o.get('door_x',0.4),zf+0.04,0.95,0.04,1.95)
                m.box('gravel',ox,zf+0.6,bw,1.2,0.04)
                for sx in (-bw/2+0.2,bw/2-0.2): m.box('frame',ox+sx,zf+0.3,0.4,0.4,0.45)   # pale guard stones at the bay's corners (AR-0024)
                m.box('dark',ox-bw/2-0.35,zf+0.08,0.08,0.08,b['eave'])   # downpipe beside the bay (AR-0024)
    elif b['id']=='stable_range':
        for i in range(5): m.box('green',b['x']-5.6+i*2.8,b['z']+d/2+0.01,1.1,0.05,2.0)
    if 'cart_porch' in b:
        p=b['cart_porch']
        if p.get('side')=='west':   # porch projects west from the barn's west wall, door facing west
            px=b['x']-w/2-p['d']/2; pz=p['z']
            m.box(wm,px,pz,p['d'],p['w'],4.0,top=False); m.gable(rm,'boards' if p.get('boarded_gable') else wm,px,pz,p['d'],p['w'],4.0,40,ridge_along='x')
            m.box('dark' if p.get('open') else 'green',px-p['d']/2-0.02,pz,0.05,3.3,3.5)   # run 3: the 1988 photograph shows the cart entry open (dark), boarded gable apex
        else:
            pz=b['z']+d/2+p['d']/2
            m.box(wm,p['x'],pz,p['w'],p['d'],4.0,top=False); m.gable(rm,wm,p['x'],pz,p['w'],p['d'],4.0,40,ridge_along='z')
            m.box('green',p['x'],pz+p['d']/2+0.02,3.3,0.05,3.5)
    for o in b.get('openings',[]):
        if o.get('side')=='west': m.box(o.get('mat','dark'),b['x']-w/2-0.02,o['z'],0.05,o['w'],o['h'],y0=o.get('y0',0.0))
        if o.get('side')=='south':   # issue #199: gable openings; arch=True draws a round head as four stepped bands
            ox,zf,y0=b['x']+o['x'],b['z']+d/2+0.02,o.get('y0',0.0); mk=o.get('mat','dark')
            m.box(mk,ox,zf,o['w'],0.05,o['h'],y0=y0)
            if o.get('arch'):
                r=o['w']/2
                for k in range(4):
                    yk=r*(k+0.5)/4; m.box(mk,ox,zf,2*math.sqrt(max(r*r-yk*yk,0.0)),0.05,r/4,y0=y0+o['h']+r*k/4)
                m.box('dressed',ox,zf-0.01,o['w']+0.5,0.04,o['h']+r+0.25,y0=y0)   # dressed-stone surround
m.mat('fieldstone',(1,1,1),0.95,tex=os.path.join(TX,'fieldstone.jpg'),tile=1.6); m.mat('fieldcope',(0.36,0.29,0.16),0.9)   # run 11 (#457): field wall stone = the 1988 barn photograph texture recoloured to the barn-and-stables painting's wall (sRGB mean 0.59/0.50/0.33, std 0.13); coping plain, the painting's lighter top course (sRGB c.0.64/0.58/0.44)
m.mat('hedge',(0.022,0.036,0.012),1.0)   # declared before the walls (run 5, #341); re-declared below with the same values
for wl in G['walls']:
    (ax,az),(bx,bz)=wl['from'],wl['to']
    if 'gate_x' in wl:
        g0,g1=wl['gate_x']; segs=[((ax,az),(g0,bz)),((g1,az),(bx,bz))]
    elif 'gate_z' in wl:
        g0,g1=wl['gate_z']; segs=[((ax,az),(bx,g0)),((ax,g1),(bx,bz))]
    else: segs=[((ax,az),(bx,bz))]
    for a,b2 in segs:
        if wl.get('kind')=='hedge': m.wall('hedge',a,b2,wl.get('h',0.9),0.9)   # run 5 (#341): the 1988 barn photograph shows grass and a low hedge on this line, not a stone wall
        else: m.wall('fieldstone' if wl.get('stone')=='field' else 'rubble',a,b2,wl.get('h',1.5),wl.get('t',0.5))   # run 6 (#340): optional height/thickness (front garden wall); run 11 (#457): pale field stone
        if wl.get('coping'): m.wall('fieldcope' if wl.get('stone')=='field' else 'dressed',a,b2,wl['coping'],wl.get('t',0.5)+0.1,y0=wl.get('h',1.5))   # run 9 (#457): coped field wall, as the barn-and-stables painting shows
    if wl.get('gate_piers'):   # forecourt gate: stone piers, ball finial on one, dark five-bar gate
        g0,g1=wl['gate_x']; z=az
        ph=wl.get('pier_h',1.9)   # run 3 (#203): piers 2.5 m with projecting caps, read against the 1.25 m gate in the house-and-gate painting
        def pyr(px,pz,hw,y,hh):   # run 6 (#203): pyramid stone cap, as on the piers in the house-and-gate painting
            c4=[(px-hw,pz-hw),(px+hw,pz-hw),(px+hw,pz+hw),(px-hw,pz+hw)]
            for k in range(4):
                (x0,z0),(x1,z1)=c4[k],c4[(k+1)%4]; m.tri('dressed',[[x0,y,z0],[px,y+hh,pz],[x1,y,z1]])
        for gx in (g0,g1): m.box('rubble',gx,z,0.9,0.9,ph); m.box('dressed',gx,z,1.1,1.1,0.16,y0=ph)
        if wl.get('pyramid_caps'):
            for gx in (g0,g1): pyr(gx,z,0.55,ph+0.16,0.45)
        fx=wl.get('finial_pier_x')
        if fx is None: m.cyl('dressed',g1,z,0.3,0.5,y0=ph+0.16,seg=12,r_top=0.12)
        else:   # run 6 (#203): the ball/urn finial stands on its own pale pier east of the gate, not on the gate pier
            fh=wl.get('finial_pier_h',ph-0.3); m.box('frame',fx,z,0.75,0.75,fh); m.box('frame',fx,z,0.95,0.95,0.14,y0=fh)
            m.cyl('frame',fx,z,0.22,0.28,y0=fh+0.14,seg=12,r_top=0.3); m.cyl('frame',fx,z,0.3,0.3,y0=fh+0.42,seg=12,r_top=0.08)
        for ex in wl.get('end_piers_x',[]):   # run 6 (#203): tall pier with a pyramid cap further along the wall
            m.box('rubble',ex,z,0.9,0.9,ph); m.box('dressed',ex,z,1.1,1.1,0.16,y0=ph); pyr(ex,z,0.55,ph+0.16,0.45)
        for k in range(5): m.box('gate',(g0+g1)/2,z,g1-g0-0.8,0.07,0.08,y0=0.25+k*0.25)
        for gx in (g0+0.45,(g0+g1)/2,g1-0.45): m.box('gate',gx,z,0.1,0.08,1.25,y0=0.1)
for y in G['yards']:
    x0,x1,z0,z1=y['gravel']; m.box('gravel',(x0+x1)/2,(z0+z1)/2,x1-x0,z1-z0,0.04)
if 'ground' in G:   # 3D model loop run 5 (issue #454): meadow ground under the group; the historic aerial and the painted plan show green fields
    gr=G['ground']; gx0,gx1,gz0,gz1=gr['extent']; gt=gr.get('thick',0.02)   # extent kept inside the model's existing bounds, so the opening camera framing does not move
    m.mat('grass',tuple(gr['rgb']),1.0); m.box('grass',(gx0+gx1)/2,(gz0+gz1)/2,gx1-gx0,gz1-gz0,gt,y0=-gt)
for gd in G.get('gardens',[]):   # run 6 (#340): planted front garden inside the garden wall (1988 farmhouse photograph)
    x0,x1,z0,z1=gd['rect']; m.mat('garden',tuple(gd.get('rgb',(0.035,0.065,0.02))),1.0); m.box('garden',(x0+x1)/2,(z0+z1)/2,x1-x0,z1-z0,gd.get('h',0.25))
    m.mat('shrub',tuple(gd.get('shrub_rgb',(0.016,0.03,0.009))),1.0)
    for (sx,sz,sr,sh_) in gd.get('shrubs',[]):   # shrub clumps of varied height: rounded (narrow foot, full middle, rounded top)
        y=gd.get('h',0.25); m.cyl('shrub',sx,sz,sr*0.55,sh_*0.45,y0=y,seg=6,r_top=sr); m.cyl('shrub',sx,sz,sr,sh_*0.55,y0=y+sh_*0.45,seg=6,r_top=sr*0.35)
for f in G.get('features',[]):
    if f['id']=='glasshouse':
        m.box('rubble',f['x'],f['z'],f['w'],f['d'],f['base'])
        m.box('pane',f['x'],f['z'],f['w'],f['d'],f['eave']-f['base'],y0=f['base'],top=False)
        m.gable('pane','pane',f['x'],f['z'],f['w'],f['d'],f['eave'],f['pitch'],ridge_along='x',over=0.05)
        if f.get('bars'):   # run 7 (#202): white glazing bars on the south face, eave rail and ridge, so the glasshouse reads above the forecourt wall (house-and-gate painting); south face only to keep the GLB small
            bw=0.07; hw,hd=f['w']/2,f['d']/2; n=max(2,int(round(f['w']/f['bars'])))
            for k in range(n+1): m.box('frame',f['x']-hw+k*f['w']/n,f['z']+hd,bw,bw,f['eave']-f['base'],y0=f['base'],top=False)
            m.box('frame',f['x'],f['z']+hd,f['w']+bw,bw,bw,y0=f['eave']-bw,top=False)
            m.box('frame',f['x'],f['z'],f['w']+0.1,bw,bw,y0=f['eave']+math.tan(math.radians(f['pitch']))*hd-bw/2)
    if f['id']=='field_gate':   # run 9 (#457): white five-bar field gate in the coped field wall (barn-and-stables painting), shut; hinge and latch posts, 4 rails, mid stile; hung on any line
        (ax_,az_),(bx_,bz_)=f['from'],f['to']; gl=math.hypot(bx_-ax_,bz_-az_); yw=math.degrees(math.atan2(bz_-az_,bx_-ax_)); ux_,uz_=(bx_-ax_)/gl,(bz_-az_)/gl
        for tt in (0.12,gl-0.12): m.box('frame',ax_+ux_*tt,az_+uz_*tt,0.16,0.16,1.35,yaw=yw)
        for k in range(4): m.box('frame',(ax_+bx_)/2,(az_+bz_)/2,gl-0.3,0.05,0.07,y0=0.25+k*0.3,yaw=yw)
        m.box('frame',(ax_+bx_)/2,(az_+bz_)/2,0.08,0.06,1.15,y0=0.2,yaw=yw)
    if f['id']=='gate_tree':
        m.cyl('bark',f['x'],f['z'],f['trunk'],f['height']*0.45,seg=10)
        if f.get('lobes'):   # run 3 (#201): broad, uneven crown as offset lobes (the painting's tree is wider than tall and leans over the gate)
            for (dx,dz,dy,rr) in f['lobes']: m.cyl('leaf',f['x']+dx,f['z']+dz,rr,rr*1.1,y0=f['height']*0.45+dy,seg=14,r_top=rr*0.55)
        else: m.cyl('leaf',f['x'],f['z'],f['crown'],f['height']*0.6,y0=f['height']*0.4,seg=16,r_top=f['crown']*0.35)
for tg in G.get('tree_groups',[]):   # run 9 (#3D aerial trees): low-poly tree masses around the group, as both aerials show (dark crowns east and south of the house, towards the church)
    m.mat('leaf2',tuple(tg.get('rgb',(0.03,0.05,0.018))),1.0)
    for (tx_,tz_,th_,tc_) in tg['trees']:
        m.cyl('bark',tx_,tz_,0.35,th_*0.4,seg=4,top=False)
        sg_=tg.get('seg',6)   # run 14 (#461): a group may ask for rounder crowns (the backdrop trees read as hexagons at 6 sides)
        if tg.get('dome'):   # run 14 (#461): four-tier domed crown so a backdrop tree reads round, not as a cone (painting's broad trees)
            for (r0_,r1_,y0_,hh_) in ((0.55,0.92,0.36,0.16),(0.92,1.0,0.52,0.14),(1.0,0.8,0.66,0.14),(0.8,0.3,0.80,0.20)):
                m.cyl('leaf2',tx_,tz_,tc_*r0_,th_*hh_,y0=th_*y0_,seg=sg_,r_top=tc_*r1_)
        else:
            m.cyl('leaf2',tx_,tz_,tc_*0.7,th_*0.3,y0=th_*0.35,seg=sg_,r_top=tc_)   # broad rounded deciduous crown (narrow foot, full middle, domed top), 6 sides to keep the GLB under its cap
            m.cyl('leaf2',tx_,tz_,tc_,th_*0.35,y0=th_*0.65,seg=sg_,r_top=tc_*0.3)
if 'church' in G:   # v0.2.1: church massing so the lane's semicircle reads (estimated)
    c=G['church']; (nl,nw),(ts,th)=c['nave'],c['tower']
    m.box('rubble',c['x'],c['z'],nl,nw,c['nave_eave'],top=False); m.gable('slate','rubble',c['x'],c['z'],nl,nw,c['nave_eave'],45,ridge_along='x')
    m.box('rubble',c['x']-nl/2-ts/2,c['z'],ts,ts,th)
m.mat('lane',(0.56,0.51,0.42),1.0); m.mat('hedge',(0.022,0.036,0.012),1.0)   # run 5: hedges darker than the new meadow ground, as both aerials show them (were lighter than the fields once the ground went in)
# photo tripods (3D model loop; the Executive 10:16 and 11:41 GMT 5 Nov 2026): a real tripod (three splayed legs, a pan head, a short
# lens barrel) at the spot and height each reference image was taken or painted from, with its field of view drawn as a translucent cone
# (heading, pitch and fov from photos.json). Aerial viewpoints get the same tripod head at altitude plus a plumb line to the ground.
PJ=os.path.join(os.path.dirname(__file__),'..','photos.json')
if os.path.exists(PJ):
    m.mat('tripod',(0.07,0.07,0.07),0.5); m.mat('tripodhead',(0.62,0.48,0.14),0.4,0.6); m.mat('tripodfov',(0.95,0.78,0.25),0.9,0.0,alpha=0.16)
    def _fov(tx,ty,tz,hd,pt,fov,Lc):
        h,p=math.radians(hd),math.radians(pt)
        dv=np.array([math.sin(h)*math.cos(p),math.sin(p),-math.cos(h)*math.cos(p)]); r=np.array([math.cos(h),0.0,math.sin(h)]); u=np.cross(r,dv)
        hw=math.tan(math.radians(fov)/2)*Lc; hv=hw*0.75; o=np.array([tx,ty,tz]); c=o+dv*Lc
        cs=[c+r*hw+u*hv,c-r*hw+u*hv,c-r*hw-u*hv,c+r*hw-u*hv]
        for k in range(4): m.tri('tripodfov',[o.tolist(),cs[k].tolist(),cs[(k+1)%4].tolist()])
    for tp in json.load(open(PJ))['tripods']:
        if tp.get('site')!='tymawr': continue
        tx,tz,hh=tp['x'],tp['z'],math.radians(tp['heading']); ty=float(tp.get('y',1.6)); aerial=ty>4
        base=ty-1.5 if aerial else 0.0; top=ty-0.12
        for k in range(3):
            a=hh+math.pi+(k-1)*2.1; fx,fz=tx+0.55*math.sin(a),tz-0.55*math.cos(a)
            m.quad('tripod',[fx-0.03,base,fz],[fx+0.03,base,fz],[tx+0.02,top,tz],[tx-0.02,top,tz]); m.quad('tripod',[fx,base,fz-0.03],[fx,base,fz+0.03],[tx,top,tz+0.02],[tx,top,tz-0.02])
        if aerial: m.box('tripod',tx,tz,0.25,0.25,base,y0=0.0)
        m.box('tripodhead',tx,tz,0.16,0.16,0.10,y0=top,yaw=math.degrees(hh))
        m.box('tripodhead',tx+0.14*math.sin(hh),tz-0.14*math.cos(hh),0.09,0.16,0.09,y0=ty-0.04,yaw=math.degrees(hh))
        _fov(tx,ty+0.01,tz,tp['heading'],tp.get('pitch',0),tp.get('fov',50),9.0 if aerial else 3.5)   # run 4: cones were 30 m (aerial) / 5 m, the aerial ones swept through the ground-level views and washed them yellow
def strip(key,a,b,wd,h=0.06,y0=0.0):
    (ax,az),(bx,bz)=a,b; m.box(key,(ax+bx)/2,(az+bz)/2,math.hypot(bx-ax,bz-az)+0.2,wd,h,y0=y0,yaw=math.degrees(math.atan2(bz-az,bx-ax)))
if 'lane_arc' in G:
    la=G['lane_arc']; (ccx,ccz),R0=la['centre'],la['radius']; a0=math.atan2(-ccz,-ccx); ha=math.radians(la['half_angle_deg']); N=48
    pts=[(ccx+R0*math.cos(a0-ha+2*ha*i/N), ccz+R0*math.sin(a0-ha+2*ha*i/N)) for i in range(N+1)]
    for p0,p1 in zip(pts,pts[1:]): strip('lane',p0,p1,la['width'],y0=0.02)
for tr in G.get('tracks',[]):
    a=tuple(tr['from'])
    if tr['to']=='arc':
        la=G['lane_arc']; (ccx,ccz),R0=la['centre'],la['radius']; dx,dz=a[0]-ccx,a[1]-ccz; k=R0/math.hypot(dx,dz); b=(ccx+dx*k,ccz+dz*k)
    else: b=tuple(tr['to'])
    strip('lane',a,b,tr['width'],y0=0.02)
    if tr.get('hedges'):
        for off in (-tr['width']/2-0.6, tr['width']/2+0.6): strip('hedge',(a[0]+off,a[1]),(b[0]+off,b[1]),0.9,1.3)
for hd in G.get('hedges',[]): strip('hedge',tuple(hd['from']),tuple(hd['to']),0.9,1.3)
if G.get('gravel_polys'):   # 3D model loop run 24 (8 Nov 2026, #467): gravel lane areas drawn as flat polygons; colour sampled from the painted reconstruction AR-0011 (sRGB median 0.66/0.55/0.44), set as a linear factor through the viewer's measured lift
    m.mat('lanegravel',(0.35,0.22,0.12),1.0)
    for gp in G['gravel_polys']:
        pts=[[float(x),float(gp.get('y',0.05)),float(z)] for x,z in gp['pts']]
        (ax_,_,az_),(bx_,_,bz_),(cx_,_,cz_)=pts[:3]
        if (bz_-az_)*(cx_-ax_)-(bx_-ax_)*(cz_-az_)<0: pts=pts[::-1]   # keep the face's normal pointing up
        m.poly('lanegravel',pts)
sizes['tymawr']=m.save(os.path.join(OUT,'tymawr.glb'),meta('tymawr',{"geometry_source":"tools/tymawr-layout.json v"+G.get('version','0.2.0')+" (Tŷ Mawr reference photographs and paintings; sizes best guess)","layout":"house and stable range face south, stable front level with the house front; west barn runs north-south and faces west","not_checked":G.get('not_checked',[]),"note":"pin = 1824 homestead-group centroid; model origin = house centre; church shown as massing only (see SITES.json)","version":G.get("version","0.2.1")}))
print(json.dumps(sizes))
