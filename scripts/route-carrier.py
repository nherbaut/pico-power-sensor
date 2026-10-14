#!/usr/bin/python3
"""Route the carrier using the existing grid router, without touching the interposer."""
import importlib.util
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/pcb/carrier'


def main():
    spec=importlib.util.spec_from_file_location('grid_router',ROOT/'scripts/route-interposer.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.OUT=OUT
    module.STEP=.1
    pcbnew=module.pcbnew
    data=json.loads((OUT/'circuit.json').read_text())
    module.NX=round(data['board']['width_mm']/module.STEP)+1
    module.NY=round(data['board']['height_mm']/module.STEP)+1
    board=pcbnew.LoadBoard(str(OUT/'carrier.kicad_pcb'))
    # Make rerouting repeatable instead of adding duplicate copper.
    for item in list(board.GetTracks()):board.Remove(item)
    class CarrierRouter(module.Router):
        def obstacles(self,net,width):
            blocked=super().obstacles(net,width)
            x0,y0,x1,y1=data['board']['antenna_keepout_mm']
            margin=width/2+.22
            import numpy as np
            gy,gx=np.ogrid[:module.NY,:module.NX]
            blocked |= (((gx*module.STEP>=x0-margin)&(gx*module.STEP<=x1+margin)) &
                        ((gy*module.STEP>=y0-margin)&(gy*module.STEP<=y1+margin)))[None,:,:]
            return blocked
    router=CarrierRouter(board)
    # Reserve a ground escape from the tightly spaced EVM connector first.
    # Otherwise surrounding signal traces can isolate it on both ground planes.
    router.route(router.pad('J_EVM',4),router.pad('J_UART',1),.25)
    groups={}
    for pad in router.pads:
        if pad.GetNumber() and pad.GetNetCode() and not pad.GetNetname().startswith('unconnected-'):
            groups.setdefault(pad.GetNetCode(),[]).append(pad)
    ground=next(net for net in board.GetNetsByNetcode().values() if net.GetNetname()=='/GND')
    # Add adjacent ground vias rather than placing drills in SMD solder pads.
    # Reserve all these before filling the two planes.
    for pad in groups[ground.GetNetCode()]:
        if pad.GetAttribute()!=pcbnew.PAD_ATTRIB_SMD:continue
        x,y=module.xy(pad.GetPosition())
        blocked=router.obstacles(ground.GetNetCode(),.6).any(axis=0)
        candidates=[(x+radius*math.cos(i*math.pi/8),y+radius*math.sin(i*math.pi/8))
                    for radius in [1.5,2,2.5,3,3.5,4] for i in range(16)]
        path_blocked=router.obstacles(ground.GetNetCode(),.2)[0]
        for vx,vy in candidates:
            ix,iy=round(vx/module.STEP),round(vy/module.STEP)
            if not (0<=ix<module.NX and 0<=iy<module.NY) or blocked[iy,ix]:continue
            # The via must clear every SMD pad, including pads on its own net.
            if any(p.GetAttribute()==pcbnew.PAD_ATTRIB_SMD and
                   p.GetBoundingBox().Contains(module.point(vx,vy)) for p in router.pads):continue
            steps=round(math.dist((x,y),(vx,vy))/.05)+1
            if any(path_blocked[round((y+(vy-y)*i/steps)/module.STEP),
                                round((x+(vx-x)*i/steps)/module.STEP)] for i in range(steps+1)):continue
            router.track(ground.GetNetCode(),[(x,y),(vx,vy)],.2)
            router.via(ground.GetNetCode(),(vx,vy));break
        else:raise RuntimeError('No ground-via location for '+pad.GetParentFootprint().GetReference())
    def priority(item):
        pads=item[1];name=pads[0].GetNetname()
        return (name=='/GND',name=='/PICO_3V3',len(pads),name)
    for code,pads in sorted(groups.items(),key=priority):
        if pads[0].GetNetname()=='/GND':continue  # Ground planes and short via connections below.
        if len(pads)<2:continue
        # Minimum spanning tree of pads, shortest branch first.
        linked=[pads[0]];remaining=pads[1:]
        while remaining:
            _,a,b=min(((math.dist(module.xy(a.GetPosition()),module.xy(b.GetPosition())),a,b)
                      for a in linked for b in remaining),key=lambda item:item[0])
            print(f'{a.GetNetname()}: {a.GetParentFootprint().GetReference()}.{a.GetNumber()} -> '
                  f'{b.GetParentFootprint().GetReference()}.{b.GetNumber()}',flush=True)
            router.route(a,b,.25 if a.GetNetname() in ['/PICO_3V3','/SD_3V3','/USB_5V'] else .2)
            linked.append(b);remaining.remove(b)
    for layer in module.LAYERS:
        for zone in list(board.Zones()):
            if not zone.GetIsRuleArea() and zone.GetLayer()==layer:board.Remove(zone)
        zone=pcbnew.ZONE(board);zone.SetLayer(layer);zone.SetNet(ground)
        zone.SetLocalClearance(pcbnew.FromMM(.25));zone.SetThermalReliefGap(pcbnew.FromMM(.25))
        zone.SetThermalReliefSpokeWidth(pcbnew.FromMM(.25));zone.SetMinThickness(pcbnew.FromMM(.2))
        poly=zone.Outline();poly.NewOutline()
        w,h=data['board']['width_mm'],data['board']['height_mm']
        for x,y in [(0,0),(w,0),(w,h),(0,h)]:
            pos=module.point(x,y);poly.Append(pos.x,pos.y)
        board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(OUT/'carrier.kicad_pcb'),board)
    # Record the 35um two-layer stackup explicitly.
    path=OUT/'carrier.kicad_pcb';s=path.read_text()
    if '(stackup' not in s:
        s=s.replace('(setup\n','''(setup
        (stackup
            (layer "F.SilkS" (type "Top Silk Screen"))
            (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
            (layer "F.Cu" (type "copper") (thickness 0.035))
            (layer "dielectric 1" (type "core") (thickness 1.51) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
            (layer "B.Cu" (type "copper") (thickness 0.035))
            (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
            (layer "B.SilkS" (type "Bottom Silk Screen"))
            (copper_finish "None") (dielectric_constraints no)
        )
''',1)
        path.write_text(s)
    data['board']['routing_status']='routed; native DRC required'
    (OUT/'circuit.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Carrier routing complete; run native ERC/DRC and parity checks.')


if __name__=='__main__':main()
