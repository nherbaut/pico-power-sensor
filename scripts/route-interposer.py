#!/usr/bin/python3
"""Route the review board, with explicit power paths and grid-based signals.

KiCad DRC is the authority for clearance/connectivity. This helper does not
replace current, footprint, mechanical or analog circuit review.
"""
import heapq
import json
import math
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
    p=ROOT/'.build/kicad'/name;p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
import numpy as np
import pcbnew

OUT=ROOT/'hardware/pcb/interposer'
STEP=.05
NX,NY=1321,921
LAYERS=[pcbnew.F_Cu,pcbnew.B_Cu]


def mm(value):return pcbnew.ToMM(value)
def point(x,y):return pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
def xy(p):return (mm(p.x),mm(p.y))


class Router:
    def __init__(self,board):
        self.escapes={}
        self.board=board
        self.mounting=json.loads((OUT/'circuit.json').read_text())['board']
        self.pads=[p for fp in board.GetFootprints() for p in fp.Pads()]
        self.byref={fp.GetReference():fp for fp in board.GetFootprints()}

    def pad(self,ref,pin):
        return next(p for p in self.byref[ref].Pads() if p.GetNumber()==str(pin))

    def track(self,net,coords,width=.25,layer=pcbnew.F_Cu):
        for a,b in zip(coords,coords[1:]):
            if a==b:continue
            t=pcbnew.PCB_TRACK(self.board);t.SetStart(point(*a));t.SetEnd(point(*b))
            if t.GetStart()==t.GetEnd():continue
            t.SetWidth(pcbnew.FromMM(width));t.SetLayer(layer);t.SetNetCode(net);self.board.Add(t)

    def via(self,net,pos):
        for existing in self.board.GetTracks():
            if isinstance(existing,pcbnew.PCB_VIA) and existing.GetNetCode()==net:
                location=xy(existing.GetPosition())
                if math.dist(location,pos)<.56:
                    for layer in LAYERS:self.track(net,[location,pos],.2,layer)
                    return
        v=pcbnew.PCB_VIA(self.board);v.SetPosition(point(*pos));v.SetWidth(pcbnew.FromMM(.6))
        v.SetDrill(pcbnew.FromMM(.3));v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(*LAYERS);v.SetNetCode(net);self.board.Add(v)

    def obstacles(self,net,width):
        blocked=np.zeros((2,NY,NX),dtype=bool)
        margin=width/2+.205+.01
        edge=int(math.ceil((margin+.3)/STEP))
        blocked[:,:edge,:]=True;blocked[:,-edge:,:]=True
        blocked[:,:,:edge]=True;blocked[:,:,-edge:]=True
        def rect(layers,x0,y0,x1,y1):
            ix0=max(0,int(math.ceil((x0-margin)/STEP)));ix1=min(NX,int(math.floor((x1+margin)/STEP))+1)
            iy0=max(0,int(math.ceil((y0-margin)/STEP)));iy1=min(NY,int(math.floor((y1+margin)/STEP))+1)
            for l in layers:blocked[l,iy0:iy1,ix0:ix1]=True
        for pad in self.pads:
            if pad.GetNetCode()==net and pad.GetNumber():continue
            active=[i for i,l in enumerate(LAYERS) if pad.GetLayerSet().Contains(l)]
            if not active:continue
            bb=pad.GetBoundingBox()
            rect(active,mm(bb.GetX()),mm(bb.GetY()),mm(bb.GetRight()),mm(bb.GetBottom()))
        for t in self.board.GetTracks():
            if t.GetNetCode()==net:continue
            if isinstance(t,pcbnew.PCB_VIA):
                x,y=xy(t.GetPosition());r=mm(t.GetWidth(pcbnew.F_Cu))/2
                r+=margin
                x0=max(0,int(math.floor((x-r)/STEP)));x1=min(NX,int(math.ceil((x+r)/STEP))+1)
                y0=max(0,int(math.floor((y-r)/STEP)));y1=min(NY,int(math.ceil((y+r)/STEP))+1)
                gy,gx=np.ogrid[y0:y1,x0:x1]
                hit=(gx*STEP-x)**2+(gy*STEP-y)**2<=r*r
                blocked[:,y0:y1,x0:x1] |= hit[None,:,:]
                continue
            a,b=xy(t.GetStart()),xy(t.GetEnd());r=mm(t.GetWidth())/2+margin
            x0=max(0,int((min(a[0],b[0])-r)/STEP));x1=min(NX,int((max(a[0],b[0])+r)/STEP)+2)
            y0=max(0,int((min(a[1],b[1])-r)/STEP));y1=min(NY,int((max(a[1],b[1])+r)/STEP)+2)
            gy,gx=np.ogrid[y0:y1,x0:x1];gx=gx*STEP;gy=gy*STEP
            dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
            frac=np.clip(((gx-a[0])*dx+(gy-a[1])*dy)/den,0,1) if den else 0
            hit=(gx-(a[0]+frac*dx))**2+(gy-(a[1]+frac*dy))**2<=r*r
            blocked[0 if t.GetLayer()==pcbnew.F_Cu else 1,y0:y1,x0:x1]|=hit
        for hole in self.mounting['mounting_holes']:
            x,y=hole['position_mm'];radius=self.mounting['mounting_keepout_diameter_mm']/2+margin
            gy,gx=np.ogrid[:NY,:NX]
            hit=(gx*STEP-x)**2+(gy*STEP-y)**2<=radius**2
            blocked |= hit[None,:,:]
        return blocked

    def route(self,a,b,width=.2):
        global STEP,NX,NY
        net=a.GetNetCode();blocked=self.obstacles(net,width)
        via_blocked=self.obstacles(net,.6).any(axis=0)
        a_escape=self.escapes.get((a.GetParentFootprint().GetReference(),a.GetNumber()))
        b_escape=self.escapes.get((b.GetParentFootprint().GetReference(),b.GetNumber()))
        startxy=a_escape or xy(a.GetPosition());endxy=b_escape or xy(b.GetPosition())
        sx,sy=[round(v/STEP) for v in startxy];ex,ey=[round(v/STEP) for v in endxy]
        starts=[(i,sx,sy) for i,l in enumerate(LAYERS) if a_escape or a.GetLayerSet().Contains(l)]
        targets={(i,ex,ey) for i,l in enumerate(LAYERS) if b_escape or b.GetLayerSet().Contains(l)}
        for l,x,y in starts+list(targets):
            if blocked[l,y,x]:
                raise RuntimeError(f'Blocked endpoint {a.GetParentFootprint().GetReference()}.{a.GetNumber()} -> {b.GetParentFootprint().GetReference()}.{b.GetNumber()}')
        distance={s:0 for s in starts};previous={};heap=[];serial=0
        def heuristic(s):return math.hypot(s[1]-ex,s[2]-ey)
        for s in starts:heapq.heappush(heap,(heuristic(s),serial,0,s));serial+=1
        done=None
        while heap:
            _,_,cost,s=heapq.heappop(heap)
            if cost!=distance.get(s):continue
            if s in targets:done=s;break
            l,x,y=s
            neighbors=[]
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                xx,yy=x+dx,y+dy
                if not (0<=xx<NX and 0<=yy<NY) or blocked[l,yy,xx]:continue
                if dx and dy and (blocked[l,y,xx] or blocked[l,yy,x]):continue
                neighbors.append(((l,xx,yy),math.sqrt(2) if dx and dy else 1))
            if not via_blocked[y,x]:neighbors.append(((1-l,x,y),35))
            for nxt,step in neighbors:
                nc=cost+step
                if nc<distance.get(nxt,float('inf')):
                    distance[nxt]=nc;previous[nxt]=s;serial+=1
                    heapq.heappush(heap,(nc+heuristic(nxt),serial,nc,nxt))
        if done is None and STEP>.025:
            coarse_grid=(STEP,NX,NY)
            # Preserve the current physical outline when refining another board.
            NX,NY=round((NX-1)*STEP/.025)+1,round((NY-1)*STEP/.025)+1
            STEP=.025
            print('Refining routing grid for dense buffer escape',flush=True)
            try:self.route(a,b,width)
            finally:STEP,NX,NY=coarse_grid
            return
        if done is None:
            pcbnew.SaveBoard(str(ROOT/'.build/hardware/failed-route.kicad_pcb'),self.board)
            raise RuntimeError(f'No route for {a.GetNetname()}: {a.GetParentFootprint().GetReference()}.{a.GetNumber()} -> {b.GetParentFootprint().GetReference()}.{b.GetNumber()}')
        nodes=[done]
        while nodes[-1] in previous:nodes.append(previous[nodes[-1]])
        nodes.reverse()
        coords=[startxy];layer=nodes[0][0];lastdir=None
        for i,(l,x,y) in enumerate(nodes):
            pos=(x*STEP,y*STEP)
            if l!=layer:
                coords.append(pos);self.track(net,coords,width,LAYERS[layer]);self.via(net,pos)
                coords=[pos];layer=l;lastdir=None
            if i+1<len(nodes) and nodes[i+1][0]==layer:
                direction=(nodes[i+1][1]-x,nodes[i+1][2]-y)
                if lastdir is not None and direction!=lastdir:coords.append(pos)
                lastdir=direction
        coords += [(nodes[-1][1]*STEP,nodes[-1][2]*STEP),endxy]
        self.track(net,coords,width,LAYERS[layer])

    def power(self):
        nc=lambda ref,pin:self.pad(ref,pin).GetNetCode()
        self.track(nc('J1',1),[(14.08,12),(14.08,13.92),(6,22)],3)
        self.track(nc('F1',2),[(28.5,22),(32.95,22),(33.95,21)],3)
        self.track(nc('Q1',1),[(40,19.095),(40,22.905)],2)
        for ref in ['Q1','Q2']:
            for n in [1,2,3]:
                p=self.pad(ref,n);x,y=xy(p.GetPosition());self.track(p.GetNetCode(),[(x,y),(40,y)],.4)
        self.track(nc('Q2',5),[(46.05,21),(46.05,23.4),(52.015,29.365)],2)
        self.track(nc('RSH1',4),[(57.985,30.635),(60,32.65)],2)
        self.track(nc('RSH1',4),[(60,32.65),(60,34),(57,37),(10,37)],3)
        for n in [2,4]:
            p=self.pad('J2',n);x,y=xy(p.GetPosition());self.track(p.GetNetCode(),[(x,37),(x,y)],1.2)

    def buffer_escape(self):
        # Reserve each dense TSSOP pad's escape before other signal routes.
        # Stagger 0.6 mm vias; 0.2 mm fingers fit the 0.65 mm pin pitch.
        for p in self.byref['U2'].Pads():
            if not p.GetNetCode():continue
            n=int(p.GetNumber());x,y=xy(p.GetPosition())
            dx=(3.5+1.2*(n%2))*(-1 if n<=8 else 1)
            if n==2:dx=-1.6 # Keep this ground via outside the supply-loop pocket.
            self.track(p.GetNetCode(),[(x,y),(x+dx,y)],.2)
            self.via(p.GetNetCode(),(x+dx,y))
            self.escapes[('U2',p.GetNumber())]=(x+dx,y)

        ground=self.pad('U2',2).GetNetCode()
        at=lambda n:self.escapes[('U2',str(n))]
        a=at(2);b=at(8)
        self.track(ground,[a,(a[0],b[1]),b],.2,pcbnew.B_Cu)

    def interface_power(self):
        for ref,target in [('R14',(22.9125,33.2)),('R15',(37.9125,33.2)),
                           ('C3',(34.95,26.2)),('C4',(41.4,24))]:
            pad=self.pad(ref,2)
            self.track(pad.GetNetCode(),[xy(pad.GetPosition()),target],.2)
            self.via(pad.GetNetCode(),target)
        for pin in [8,10,11]:
            pad=self.pad('J2',pin);x,y=xy(pad.GetPosition())
            target=(x,39.05 if pin!=11 else 44)
            self.track(pad.GetNetCode(),[(x,y),target],.2,pcbnew.B_Cu)
            self.via(pad.GetNetCode(),target)
            self.escapes[('J2',str(pin))]=target
        for ref,pin,target in [('R11',2,(25.3,29.95)),('R14',1,(20.2,32))]:
            pad=self.pad(ref,pin)
            self.track(pad.GetNetCode(),[xy(pad.GetPosition()),target],.2)
            self.via(pad.GetNetCode(),target)
            self.escapes[(ref,str(pin))]=target
        net=self.pad('U2',1).GetNetCode()
        # Reserve the external 3V3 distribution before UART routes fence it in.
        self.track(net,[(16,32),(17.5,30.6),(26.5,30.6),(26.5,35.1),(32.0875,35.1)])
        for x in [28.0875,32.0875]:self.track(net,[(x,35.1),(x,34)])
        self.track(net,[(27.2,26.725),(27.2,28.025)])
        self.track(net,[(27.2,28.025),(26.3,28.025),(26.3,30.6)],layer=pcbnew.B_Cu)
        self.via(net,(26.3,30.6));self.track(net,[(26.3,30.6),(26.5,30.6)])
        self.track(net,[(33.05,25),(31.9,26.725)])

    def signals(self):
        groups={}
        for pad in self.pads:
            if pad.GetNumber() and pad.GetNetCode() and pad.GetNetname()!='GND':
                groups.setdefault(pad.GetNetCode(),[]).append(pad)
        # Power paths are already connected; attach small-signal branches only.
        skip={'VIN_RAW','COMMON_SOURCE','PICO_3V3'}
        priority=['PROTECTED','VIN_FUSED','OV','SHDN','UV','GATE_DRV','SENSE_PLUS','SENSE_MINUS','PICO_3V3','GPIO17','GPIO15','GPIO14','PICO_TX','PICO_RX','PICO_MARK','PI_5V','PI_3V3','GATE_Q1','GATE_Q2','GATE_RC']
        ordered=sorted(groups.items(),key=lambda item:priority.index(item[1][0].GetNetname()) if item[1][0].GetNetname() in priority else 100)
        for net,pads in ordered:
            pads.sort(key=lambda p:(p.GetParentFootprint().GetReference()!='U1',p.GetParentFootprint().GetReference(),int(p.GetNumber())))
            name=pads[0].GetNetname()
            if len(pads)<2 or name in skip:continue
            if name=='VIN_FUSED':
                root=self.pad('Q1',5);pending=[p for p in pads if p.GetParentFootprint().GetReference() not in ['Q1','F1']]
            elif name=='PROTECTED':
                root=self.pad('Q2',5);pending=[p for p in pads if p.GetParentFootprint().GetReference() not in ['Q2','RSH1']]
            elif name=='PI_5V':
                root=self.pad('J2',4);pending=[p for p in pads if p.GetParentFootprint().GetReference() not in ['J2','RSH1']]
            else:root=pads[0];pending=pads[1:]
            connected=[root]
            while pending:
                a,b=min(((a,b) for a in pending for b in connected),
                        key=lambda pair:math.dist(xy(pair[0].GetPosition()),xy(pair[1].GetPosition())))
                self.route(a,b);pending.remove(a);connected.append(a)
            print('Routed',name,flush=True)

    def ground_connections(self):
        code=self.pad('J1',2).GetNetCode()
        grounded=[p for p in self.pads if p.GetNetCode()==code and p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH]
        # Dense header clearances can isolate a grounded plated hole on both
        # copper layers. Explicitly connect every return contact before pouring.
        connected=[self.pad('J1',2)];pending=[p for p in grounded if p!=connected[0]]
        while pending:
            pad,target=min(((p,t) for p in pending for t in connected),
                           key=lambda pair:math.dist(xy(pair[0].GetPosition()),xy(pair[1].GetPosition())))
            self.route(pad,target);pending.remove(pad);connected.append(pad)
        for pad in self.pads:
            if pad.GetNetCode()==code and pad.GetAttribute()==pcbnew.PAD_ATTRIB_SMD and pad.GetParentFootprint().GetReference() not in ['U2','R14','R15','C3','C4']:
                target=min(grounded,key=lambda p:math.dist(xy(p.GetPosition()),xy(pad.GetPosition())))
                self.route(pad,target)
    def ground_pours(self):
        code=self.pad('J1',2).GetNetCode()
        blocked=self.obstacles(code,.6).any(axis=0)
        for y in range(3,36,4):
            for x in range(3,64,4):
                if not blocked[round(y/STEP),round(x/STEP)]:self.via(code,(x,y))
        for layer in LAYERS:
            z=pcbnew.ZONE(self.board)
            layer_set=pcbnew.LSET();layer_set.AddLayer(layer);z.SetLayerSet(layer_set)
            z.SetNetCode(code)
            z.SetLocalClearance(pcbnew.FromMM(.2));z.SetMinThickness(pcbnew.FromMM(.2))
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
            poly=z.Outline();poly.NewOutline()
            for x,y in [(0.5,.5),(65.5,.5),(65.5,45.5),(.5,45.5)]:poly.Append(int(pcbnew.FromMM(x)),int(pcbnew.FromMM(y)))
            self.board.Add(z)
        self.board.BuildConnectivity()
        pcbnew.ZONE_FILLER(self.board).Fill(self.board.Zones())
        self.board.BuildConnectivity()
        connectivity=self.board.GetConnectivity()
        unused=[t for t in self.board.GetTracks() if isinstance(t,pcbnew.PCB_VIA)
                and t.GetNetCode()!=code
                and not all(connectivity.IsConnectedOnLayer(t,l) for l in LAYERS)]
        for via in unused:
            center=xy(via.GetPosition())
            # Removing a via must preserve same-layer junctions formed by its disk.
            for t in list(connectivity.GetConnectedTracks(via)):
                if isinstance(t,pcbnew.PCB_VIA):continue
                a,b=xy(t.GetStart()),xy(t.GetEnd());dx=b[0]-a[0];dy=b[1]-a[1]
                length=dx*dx+dy*dy
                fraction=max(0,min(1,((center[0]-a[0])*dx+(center[1]-a[1])*dy)/length)) if length else 0
                closest=(a[0]+fraction*dx,a[1]+fraction*dy)
                self.track(via.GetNetCode(),[center,closest],.2,t.GetLayer())
            self.board.Remove(via)
        self.board.BuildConnectivity()


def main():
    board=pcbnew.LoadBoard(str(OUT/'interposer.kicad_pcb'))
    if not board:raise SystemExit('Cannot load board')
    if list(board.GetTracks()) or any(not z.GetIsRuleArea() for z in board.Zones()):raise SystemExit('Refusing to overwrite routed board; regenerate/review deliberately first.')
    router=Router(board);router.power();router.buffer_escape();router.interface_power();router.signals();router.ground_connections();router.ground_pours()
    pcbnew.SaveBoard(str(OUT/'interposer.kicad_pcb'),board)
    data=json.loads((OUT/'circuit.json').read_text());data['board']['routing_status']='routed; DRC and bench review required'
    (OUT/'circuit.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Saved routed review board. Run KiCad DRC; no fabrication release implied.')


if __name__=='__main__':main()
