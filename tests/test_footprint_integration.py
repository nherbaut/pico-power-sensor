"""Protect manufacturer pad dimensions across native CAD and regeneration paths."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FootprintIntegrationTests(unittest.TestCase):
    def test_native_and_generated_reviewed_geometry(self):
        program = r'''
import importlib.util, sys
from pathlib import Path
import pcbnew
sys.path.insert(0,str(Path.cwd()/'scripts'))
from footprint_corrections import led, shunt
def load(name):
    spec=importlib.util.spec_from_file_location(name,Path('scripts')/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
interposer=load('generate-interposer')
carrier=load('generate-carrier')
assert interposer.pads_for('LED_0805')==[('1',-1.175,0,1.25,1.1,0),('2',1.175,0,1.25,1.1,0)]
sense={p[0]:p for p in interposer.pads_for('WSK2512_5m_Kelvin')}
assert sense['2'][1:5]==(-3.28,1.27,1.7,.76)
assert sense['3'][1:5]==(3.28,-1.27,1.7,.76)
assert '(start -8.3 -1.25)' in carrier.evm_footprint()
for name,library in [('interposer','PicoPower.pretty'),('carrier','Carrier.pretty')]:
    folder=Path('hardware/pcb')/name
    board=pcbnew.LoadBoard(str(folder/(name+'.kicad_pcb')))
    for fp in board.GetFootprints():
        ref=fp.GetReference()
        if ref.startswith('D'):
            for pad in fp.Pads():
                assert abs(pcbnew.ToMM(pad.GetSize().x)-1.25)<1e-6
                assert abs(pcbnew.ToMM(pad.GetSize().y)-1.10)<1e-6
                assert abs(abs(pcbnew.ToMM(pad.GetFPRelativePosition().x))-1.175)<1e-6
                if pad.GetNumber()=='1':assert pad.GetNetname()=='/GND'
        if ref=='RSH1':
            for pad in fp.Pads():
                if pad.GetNumber() in ('2','3'):
                    assert abs(pcbnew.ToMM(pad.GetSize().x)-1.70)<1e-6
                    assert abs(abs(pcbnew.ToMM(pad.GetFPRelativePosition().x))-3.28)<1e-6
        if ref=='J_EVM':
            rect=next(g for g in fp.GraphicalItems() if isinstance(g,pcbnew.PCB_SHAPE) and g.GetLayer()==pcbnew.F_Fab)
            assert abs(abs(pcbnew.ToMM(rect.GetEnd().x-rect.GetStart().x))-4.85)<1e-6
    # Correcting a freshly loaded stock footprint twice must retain the dimensions.
    fp=pcbnew.FootprintLoad('/usr/share/kicad/footprints/LED_SMD.pretty','LED_0805_2012Metric')
    led(fp);led(fp)
    assert len([g for g in fp.GraphicalItems() if g.GetLayer()==pcbnew.F_CrtYd])==1
    local=pcbnew.FootprintLoad(str(folder/library),'LED_0805')
    assert all(abs(pcbnew.ToMM(p.GetSize().x)-1.25)<1e-6 for p in local.Pads())
'''
        result = subprocess.run(['/usr/bin/python3', '-c', program], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
