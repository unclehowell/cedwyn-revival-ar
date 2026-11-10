
"""Minimal GLB writer (numpy only) for the Revival AR models. x=east, y=up, z=south, metres."""
import json, struct, math
import numpy as np

class Model:
    def __init__(self, name):
        self.name=name; self.mats={}; self.geo={}
    def mat(self, key, rgb, rough=0.85, metal=0.0, alpha=1.0, double=False, tex=None, tile=2.0):
        """tex: path to a small jpg (<=256 KB) embedded in the GLB; tile: metres per texture repeat (box-projected UVs)."""
        self.mats[key]=dict(rgb=rgb,rough=rough,metal=metal,alpha=alpha,double=double,tex=tex,tile=tile); self.geo.setdefault(key,[[],[],[]])
    def tri(self, key, pts, n=None):
        P,N,I=self.geo[key]; base=len(P)
        pts=[np.array(p,float) for p in pts]
        if n is None:
            n=np.cross(pts[1]-pts[0],pts[2]-pts[0]); l=np.linalg.norm(n); n=n/l if l>0 else np.array([0,1,0.])
        for p in pts: P.append(p); N.append(n)
        I.extend([base,base+1,base+2])
    def quad(self, key, a,b,c,d):
        self.tri(key,[a,b,c]); self.tri(key,[a,c,d])
    def poly(self,key,pts):  # convex fan
        for i in range(1,len(pts)-1): self.tri(key,[pts[0],pts[i],pts[i+1]])
    # --- primitives ---
    def box(self,key,cx,cz,w,d,h,y0=0.0,yaw=0.0,top=True):
        """w along local x, d along local z, yaw degrees clockwise from north (rotates local axes)."""
        c,s=math.cos(math.radians(yaw)),math.sin(math.radians(yaw))
        def T(x,y,z): return [cx+x*c-z*s, y, cz+x*s+z*c]
        x0,x1,z0,z1=-w/2,w/2,-d/2,d/2; y1=y0+h
        q=[[(x0,z1),(x1,z1)],[(x1,z1),(x1,z0)],[(x1,z0),(x0,z0)],[(x0,z0),(x0,z1)]]
        for (ax,az),(bx,bz) in q:
            self.quad(key,T(ax,y0,az),T(bx,y0,bz),T(bx,y1,bz),T(ax,y1,az))
        if top: self.quad(key,T(x0,y1,z1),T(x1,y1,z1),T(x1,y1,z0),T(x0,y1,z0))
    def gable(self,key_roof,key_wall,cx,cz,w,d,eave,pitch,yaw=0.0,ridge_along='x',over=0.3,hip0=None,hip1=None):
        """Gabled roof over a w x d footprint at height eave; ridge along local x (or z)."""
        c,s=math.cos(math.radians(yaw)),math.sin(math.radians(yaw))
        def T(x,y,z): return [cx+x*c-z*s, y, cz+x*s+z*c]
        if ridge_along=='x': L,S=w/2+over,d/2+over; span=d/2
        else: L,S=d/2+over,w/2+over; span=w/2
        rh=math.tan(math.radians(pitch))*span; ry=eave+rh
        def U(a,y,b): return T(a,y,b) if ridge_along=='x' else T(b,y,a)
        e=eave-over*math.tan(math.radians(pitch))
        Lg=L-over
        if hip0 or hip1:   # hipped ends (3D model loop: run 3, 5 Nov 2026, house west end from the 1988 photograph = hip0 at the -L end; run 26, 9 Nov 2026, #467, pantile range east end from AR-0011 = hip1 at the +L end); pitches in degrees
            xa=-Lg+rh/math.tan(math.radians(hip0)) if hip0 else -L
            xb=Lg-rh/math.tan(math.radians(hip1)) if hip1 else L
            self.quad(key_roof,U(-L,e,S),U(L,e,S),U(xb,ry,0),U(xa,ry,0))
            self.quad(key_roof,U(L,e,-S),U(-L,e,-S),U(xa,ry,0),U(xb,ry,0))
            if hip0: self.tri(key_roof,[U(-L,e,-S),U(-L,e,S),U(xa,ry,0)]); self.hip_ridge=xa
            if hip1: self.tri(key_roof,[U(L,e,S),U(L,e,-S),U(xb,ry,0)]); self.hip_ridge1=xb
        else:
            self.quad(key_roof,U(-L,e,S),U(L,e,S),U(L,ry,0),U(-L,ry,0))
            self.quad(key_roof,U(L,e,-S),U(-L,e,-S),U(-L,ry,0),U(L,ry,0))
        for sx in tuple(v for v,h in ((-Lg,hip0),(Lg,hip1)) if not h):
            pts=[U(sx,eave,span),U(sx,eave,-span),U(sx,ry,0)]
            if sx<0: pts=pts[::-1]
            self.tri(key_wall,pts)
        return ry
    def cyl(self,key,cx,cz,r,h,y0=0.0,seg=24,top=True,r_top=None):
        rt=r if r_top is None else r_top
        for i in range(seg):
            a0=2*math.pi*i/seg; a1=2*math.pi*(i+1)/seg
            p0=[cx+r*math.cos(a0),y0,cz+r*math.sin(a0)]; p1=[cx+r*math.cos(a1),y0,cz+r*math.sin(a1)]
            q0=[cx+rt*math.cos(a0),y0+h,cz+rt*math.sin(a0)]; q1=[cx+rt*math.cos(a1),y0+h,cz+rt*math.sin(a1)]
            if rt>1e-6: self.quad(key,p0,q0,q1,p1)
            else: self.tri(key,[p0,q0,p1])
            if top and rt>1e-6: self.tri(key,[[cx,y0+h,cz],q1,q0])
    def ringwall(self,key,cx,cz,r,h,t,seg=48,y0=0.0,gap=None):
        for i in range(seg):
            a=(i+0.5)/seg*2*math.pi
            if gap and abs(((math.degrees(a)-gap[0]+180)%360)-180)<gap[1]/2: continue
            L=2*math.pi*r/seg*1.04
            self.box(key,cx+r*math.cos(a),cz+r*math.sin(a),t,L,h,y0=y0,yaw=math.degrees(a))
    def wall(self,key,a,b,h,t,y0=0.0):
        (ax,az),(bx,bz)=a,b; L=math.hypot(bx-ax,bz-az)
        yaw=math.degrees(math.atan2(bz-az,bx-ax))
        self.box(key,(ax+bx)/2,(az+bz)/2,L,t,h,y0=y0,yaw=yaw)
    # --- export ---
    def save(self,path,extras=None):
        bufs=bytearray(); views=[]; accs=[]; prims=[]; mats=[]; images=[]; textures=[]
        def add(arr,target):
            nonlocal bufs
            while len(bufs)%4: bufs+=b'\0'
            off=len(bufs); b=arr.tobytes(); bufs+=b
            views.append({"buffer":0,"byteOffset":off,"byteLength":len(b),**({"target":target} if target else {})}); return len(views)-1
        for mi,(k,m) in enumerate(self.mats.items()):
            pbr={"baseColorFactor":list(m['rgb'])+[m['alpha']],"metallicFactor":m['metal'],"roughnessFactor":m['rough']}
            if m.get('tex'):   # photo-sampled texture (3D model loop, realism pass): factor is a tint, the image carries the colour
                iv=add(np.frombuffer(open(m['tex'],'rb').read(),np.uint8),None); views[iv].pop('target',None)
                images.append({"bufferView":iv,"mimeType":"image/jpeg"}); textures.append({"source":len(images)-1,"sampler":0})
                pbr["baseColorTexture"]={"index":len(textures)-1}
            mats.append({"name":k,"pbrMetallicRoughness":pbr,
                         "doubleSided":True, **({"alphaMode":"BLEND"} if m['alpha']<1 else {})})
            P,N,I=self.geo[k]
            if not I: continue
            P=np.array(P,np.float32); N=np.array(N,np.float32)
            PN=np.ascontiguousarray(np.hstack([P,N])); _,first,inv=np.unique(PN.view(np.dtype((np.void,24))).ravel(),return_index=True,return_inverse=True)   # 3D model loop run 13: weld identical (position, normal) vertices (lossless; quads drop 6 -> 4 vertices)
            order=np.argsort(first); remap=np.empty_like(order); remap[order]=np.arange(len(order)); P=P[first[order]]; N=N[first[order]]; I=remap[inv.ravel()[np.asarray(I)]]
            I=np.array(I,np.uint16 if len(P)<65536 else np.uint32)   # 3D model loop run 9: 16-bit indices where they fit (lossless, about a sixth off the GLB)
            vp=add(P,34962); accs.append({"bufferView":vp,"componentType":5126,"count":len(P),"type":"VEC3","min":P.min(0).tolist(),"max":P.max(0).tolist()}); ap=len(accs)-1
            vn=add(N,34962); accs.append({"bufferView":vn,"componentType":5126,"count":len(N),"type":"VEC3"}); an=len(accs)-1
            vi=add(I,34963); accs.append({"bufferView":vi,"componentType":(5123 if I.dtype==np.uint16 else 5125),"count":len(I),"type":"SCALAR"}); ai=len(accs)-1
            att={"POSITION":ap,"NORMAL":an}
            if m.get('tex'):   # box-projected UVs: drop the dominant normal axis, metres / tile
                ax=np.abs(N).argmax(1); t=float(m['tile'])
                U=np.where(ax==0,P[:,2],P[:,0]); V=np.where(ax==1,P[:,2],-P[:,1])
                UV=(np.stack([U,V],1)/t).astype(np.float32)
                vu=add(UV,34962); accs.append({"bufferView":vu,"componentType":5126,"count":len(UV),"type":"VEC2"}); att["TEXCOORD_0"]=len(accs)-1
            prims.append({"attributes":att,"indices":ai,"material":mi})
        gl={"asset":{"version":"2.0","generator":"cedwyn revival glb.py — Sion's Tab agent"},"scene":0,"scenes":[{"nodes":[0],"name":self.name}],
            "nodes":[{"mesh":0,"name":self.name,**({"extras":extras} if extras else {})}],"meshes":[{"name":self.name,"primitives":prims}],
            "materials":mats,**({"images":images,"textures":textures,"samplers":[{"magFilter":9729,"minFilter":9987,"wrapS":10497,"wrapT":10497}]} if images else {}),"accessors":accs,"bufferViews":views,"buffers":[{"byteLength":len(bufs)}]}
        if extras: gl["asset"]["extras"]=extras
        js=json.dumps(gl,ensure_ascii=False).encode('utf8'); js+=b' '*((4-len(js)%4)%4)
        while len(bufs)%4: bufs+=b'\0'
        out=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(bufs))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(bufs),0x004E4942)+bytes(bufs)
        open(path,'wb').write(out); return len(out)
