"""Reference calculations with explicit conditions, never bench measurements."""
import itertools


def threshold_corners(bottom=10000, middle=1500, top=95300,
                      tolerance=.001, tcr=25e-6, excursion_C=45, leakage_A=10e-9):
    # 10..70 C component assumption includes heating above 10..40 C ambient.
    error = (1+tolerance)*(1+tcr*excursion_C)-1
    values = {key: [] for key in ('uv_trip', 'uv_restart', 'ov_trip', 'ov_restart')}
    for sb, sm, st, io, iu, threshold, hysteresis in itertools.product(
            (-1,1), (-1,1), (-1,1), (-leakage_A,leakage_A),
            (-leakage_A,leakage_A), (.4925,.5075), (.020,.032)):
        rb, rm, rt = bottom*(1+sb*error), middle*(1+sm*error), top*(1+st*error)
        for key in values:
            v = threshold + (hysteresis if key=='uv_restart' else -hysteresis if key=='ov_restart' else 0)
            if key.startswith('ov'):
                vm = v + rm*(v/rb+io)
                vin = vm + rt*(v/rb+io+iu)
            else:
                vb = (v-rm*io)/(1+rm/rb)
                vin = v + rt*(vb/rb+io+iu)
            values[key].append(vin)
    return {key: [min(v), max(v)] for key,v in values.items()}


def supplemental_analysis():
    cmin = 12e-9 * .95 * (1-30e-6*45)
    slew = 60e-6/cmin
    return dict(
        evidence_type='design calculation; not measured or a complete safety bound',
        ambient_C=[10,40], assumed_component_temperature_C=[10,70],
        component_temperature_requires_validation=True,
        threshold_corners_with_independent_tolerance_drift_leakage_V=threshold_corners(),
        threshold_limitations='10 nA leakage specified at VIN=60V; hysteresis at 12V; verify application at 5.1V; ageing and dynamic overshoot excluded',
        inrush=dict(gate_current_reference_A=[20e-6,35e-6,60e-6],
                    gate_current_test_condition='VIN=VOUT=12 V, GATE=15 V; verify at 5.1 V',
                    external_gate_capacitance_min_F=cmin,
                    simplified_upper_reference_slew_V_per_ms=slew/1000,
                    loads=[dict(capacitance_uF=c, charging_current_reference_A=c*1e-6*slew,
                                stored_energy_at_5_1V_J=.5*c*1e-6*5.1**2)
                           for c in (100,330,470,1000)],
                    soa_verified=False,
                    limitations='Source-follower approximation excludes load current, intrinsic capacitance, MOSFET SOA and supply limiting; actual Pi/HAT capacitance unknown'),
        sd_ldo=dict(input_max_assumption_V=5.25, output_min_reference_V=3.3*.99,
                    average_current_design_screen_A=.15,
                    reference_dissipation_W=(5.25-3.3*.99)*.15,
                    reference_junction_C=40+(5.25-3.3*.99)*.15*231.1,
                    basis='DBV JEDEC thetaJA=231.1 C/W; 1% output reference, excludes IQ and actual PCB thermal resistance; not a rating',
                    continuous_500mA_approved=False,
                    actual_card_peak_average_and_transients_required=True),
        drop_screen=dict(reference_known_subtotal_mV=96.625,
                         remaining_before_holder_header_copper_hot_effects_mohm=.675,
                         basis='5.025 mOhm shunt + 2.8 mOhm MOSFETs + 9.5 mOhm cold fuse + 2 mOhm input contact reference',
                         complete=False),
        fault_policy=dict(operator_abort=True,hardware_latch=False,automatic_reconnection_possible=True,
                          fault_pin_connected=False,manual_power_cycle_validated=False))
