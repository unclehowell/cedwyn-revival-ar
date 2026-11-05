
import sys, math, json, os
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
m.mat('brick',(0.20,0.06,0.035),0.85); m.mat('green',(0.16,0.33,0.2),0.6); m.mat('gravel',(0.33,0.30,0.25),1.0); m.mat('glass',(0.04,0.045,0.05),0.35,0.0)
m.mat('dark',(0.08,0.08,0.08),0.9); m.mat('boards',(0.42,0.40,0.35),0.9); m.mat('gate',(0.10,0.11,0.10),0.7); m.mat('pane',(0.75,0.85,0.85),0.1,0.0,0.45); m.mat('bark',(0.30,0.22,0.15),0.95); m.mat('leaf',(0.24,0.36,0.18),1.0)
WM={'limewash':'limewash','rubble stone':'rubble','dressed stone':'dressed'}; RM={'slate':'slate','red pantile':'pantile'}
for b in G['buildings']:
    if b['id']=='church': continue
    wm=WM.get(b.get('walls'),'limewash'); rm=RM.get(b.get('roof'),'slate')
    if b['id'].startswith('stone_barn'): rm='slate_barn'   # the 1988 barn photograph: paler, weathered slate
    if 'len_ew' in b: w,d,ridge=b['len_ew'],b['dep_ns'],'x'
    else: w,d,ridge=b['dep_ew'],b['len_ns'],'z'
    m.box(wm,b['x'],b['z'],w,d,b['eave'],top=False)
    ry=m.gable(rm,wm,b['x'],b['z'],w,d,b['eave'],b['pitch'],ridge_along=ridge,hip0=b.get('hip_west_pitch'))
    for ch in b.get('chimneys',[]):   # 'x' (offset from the building centre), 'w', 'd', 'h' (height above the ridge): measured from the 1988 photograph (3D model loop run 3)
        at=ch.get('at') or ('left' if ch.get('x',0)<1 else 'right')
        cxx={'left':b['x']-w/2+0.5,'centre':b['x'],'right':b['x']+w/2-0.5}[at]
        if 'x' in ch: cxx=b['x']+ch['x']
        h0=ry-1.2 if ('x' in ch or at=='centre') else b['eave']
        cw,cd,chh=ch.get('w',0.9),ch.get('d',1.0),ch.get('h',1.0)
        m.box('brick' if 'brick' in ch['mat'] else 'rubble',cxx,b['z'],cw,cd,ry-h0+chh,y0=h0)
        m.box('brick' if 'brick' in ch['mat'] else 'rubble',cxx,b['z'],cw+0.12,cd+0.12,0.15,y0=ry+chh-0.25)   # projecting cap course
    if 'chimney' in b: m.box('rubble',b['x'],b['z']-d/2+0.6,1.0,0.9,ry-b['eave']+1.0,y0=b['eave'])
    if b.get('ridge_tiles'):   # red clay ridge tiles (1988 photographs of house and barn)
        if ridge=='x' and b.get('hip_west_pitch'):   # hipped west end: ridge tiles from the hip apex east, plus the two hip lines
            xr=b['x']+m.hip_ridge; xe=b['x']+w/2+0.3; m.box('ridge',(xr+xe)/2,b['z'],xe-xr,0.32,0.2,y0=ry-0.08)
            for sz in (1,-1):
                a=[b['x']-w/2,b['eave'],b['z']+sz*d/2]; c=[xr,ry,b['z']]
                mid=[(a[0]+c[0])/2,(a[1]+c[1])/2,(a[2]+c[2])/2]; ln=math.dist(a,c)
                hor=math.hypot(c[0]-a[0],c[2]-a[2]); yaw=math.degrees(math.atan2(c[2]-a[2],c[0]-a[0]))
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
        for sx in (-p['w']/2+0.1,p['w']/2-0.1): m.box('timber',px+sx,pz+p['d']/2-0.1,0.14,0.14,2.3)
        m.box('timber',px,pz+p['d']/2-0.1,p['w'],0.16,0.18,y0=2.25)
        m.gable('slate','timber',px,pz,p['w'],p['d'],2.4,40,ridge_along='z',over=0.15)
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
    if b['id']=='stable_range':
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
for wl in G['walls']:
    (ax,az),(bx,bz)=wl['from'],wl['to']
    if 'gate_x' in wl:
        g0,g1=wl['gate_x']; segs=[((ax,az),(g0,bz)),((g1,az),(bx,bz))]
    elif 'gate_z' in wl:
        g0,g1=wl['gate_z']; segs=[((ax,az),(bx,g0)),((ax,g1),(bx,bz))]
    else: segs=[((ax,az),(bx,bz))]
    for a,b2 in segs: m.wall('rubble',a,b2,1.5,0.5)
    if wl.get('gate_piers'):   # forecourt gate: stone piers, ball finial on one, dark five-bar gate
        g0,g1=wl['gate_x']; z=az
        ph=wl.get('pier_h',1.9)   # run 3 (#203): piers 2.5 m with projecting caps, read against the 1.25 m gate in the house-and-gate painting
        for gx in (g0,g1): m.box('rubble',gx,z,0.9,0.9,ph); m.box('dressed',gx,z,1.1,1.1,0.16,y0=ph)
        m.cyl('dressed',g1,z,0.3,0.5,y0=ph+0.16,seg=12,r_top=0.12)
        for k in range(5): m.box('gate',(g0+g1)/2,z,g1-g0-0.8,0.07,0.08,y0=0.25+k*0.25)
        for gx in (g0+0.45,(g0+g1)/2,g1-0.45): m.box('gate',gx,z,0.1,0.08,1.25,y0=0.1)
for y in G['yards']:
    x0,x1,z0,z1=y['gravel']; m.box('gravel',(x0+x1)/2,(z0+z1)/2,x1-x0,z1-z0,0.04)
for f in G.get('features',[]):
    if f['id']=='glasshouse':
        m.box('rubble',f['x'],f['z'],f['w'],f['d'],f['base'])
        m.box('pane',f['x'],f['z'],f['w'],f['d'],f['eave']-f['base'],y0=f['base'],top=False)
        m.gable('pane','pane',f['x'],f['z'],f['w'],f['d'],f['eave'],f['pitch'],ridge_along='x',over=0.05)
    if f['id']=='gate_tree':
        m.cyl('bark',f['x'],f['z'],f['trunk'],f['height']*0.45,seg=10)
        if f.get('lobes'):   # run 3 (#201): broad, uneven crown as offset lobes (the painting's tree is wider than tall and leans over the gate)
            for (dx,dz,dy,rr) in f['lobes']: m.cyl('leaf',f['x']+dx,f['z']+dz,rr,rr*1.1,y0=f['height']*0.45+dy,seg=14,r_top=rr*0.55)
        else: m.cyl('leaf',f['x'],f['z'],f['crown'],f['height']*0.6,y0=f['height']*0.4,seg=16,r_top=f['crown']*0.35)
if 'church' in G:   # v0.2.1: church massing so the lane's semicircle reads (estimated)
    c=G['church']; (nl,nw),(ts,th)=c['nave'],c['tower']
    m.box('rubble',c['x'],c['z'],nl,nw,c['nave_eave'],top=False); m.gable('slate','rubble',c['x'],c['z'],nl,nw,c['nave_eave'],45,ridge_along='x')
    m.box('rubble',c['x']-nl/2-ts/2,c['z'],ts,ts,th)
m.mat('lane',(0.56,0.51,0.42),1.0); m.mat('hedge',(0.20,0.33,0.15),1.0)
# photo tripods (3D model loop, the Executive's 10:16 direction 5 Nov 2026): one small tripod where each published photograph was taken
# (photos.json beside SITES.json; positions estimated by matching the photograph to the model); the viewer puts a tappable marker on each.
PJ=os.path.join(os.path.dirname(__file__),'..','photos.json')
if os.path.exists(PJ):
    m.mat('tripod',(0.05,0.05,0.05),0.5); m.mat('tripodcam',(0.55,0.42,0.12),0.4,0.6)
    for tp in json.load(open(PJ))['tripods']:
        if tp.get('site')!='tymawr': continue
        tx,tz,hh=tp['x'],tp['z'],math.radians(tp['heading'])
        for k in range(3):
            a=hh+math.pi+(k-1)*2.1; fx,fz=tx+0.55*math.sin(a),tz-0.55*math.cos(a)
            m.quad('tripod',[fx-0.03,0,fz],[fx+0.03,0,fz],[tx+0.02,1.45,tz],[tx-0.02,1.45,tz]); m.quad('tripod',[fx,0,fz-0.03],[fx,0,fz+0.03],[tx,1.45,tz+0.02],[tx,1.45,tz-0.02])
        m.box('tripodcam',tx+0.12*math.sin(hh),tz-0.12*math.cos(hh),0.34,0.22,0.24,y0=1.45,yaw=math.degrees(hh))
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
sizes['tymawr']=m.save(os.path.join(OUT,'tymawr.glb'),meta('tymawr',{"geometry_source":"tools/tymawr-layout.json v"+G.get('version','0.2.0')+" (Tŷ Mawr reference photographs and paintings; sizes best guess)","layout":"house and stable range face south, stable front level with the house front; west barn runs north-south and faces west","not_checked":G.get('not_checked',[]),"note":"pin = 1824 homestead-group centroid; model origin = house centre; church shown as massing only (see SITES.json)","version":G.get("version","0.2.1")}))
print(json.dumps(sizes))
