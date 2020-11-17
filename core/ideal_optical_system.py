from core.srw_importer import *
from core.default_values import *

old_parameters = [[0, 0, 1.0, 0, 0, 1.0, 1.0, 1.0, 1.0, 0, 0.0, 0.0],
                  [0, 0, 1.0, 0, 0, 1.0, 1.0, 1.0, 1.0, 0, 0.0, 0.0],
                  [0, 0, 1.0, 1, 0, 1.0,  1.0, 1.0, 1.0, 0, 0.0, 0.0],
                  [0, 0, 1.0, 0, 0, 1.0,  5.0, 1.0, 5.0, 0, 0.0, 0.0],
                  [0, 0, 1.0, 1, 0, 0.75, 2.0, 0.5, 2.0, 0, 0.0, 0.0]]

auto_parameters = [[0, 0, 1.0, 0, 0, 1.0, 1.0, 1.0, 1.0, 0, 0.0, 0.0],
                   [0, 0, 1.0, 0, 0, 1.0, 1.0, 1.0, 1.0, 0, 0.0, 0.0],
                   [0, 0, 1.0, 1, 0, 1.0, 1.0, 1.0, 1.0, 0, 0.0, 0.0],
                   [0, 0, 1.0, 0, 0, 1.0, 1.0, 1.0, 1.0, 0, 0.0, 0.0],
                   [0, 0, 1.0, 1, 0, 1.0, 5.0, 1.0, 5.0, 0, 0.0, 0.0]]

def get_beamline(f1=src_to_oe1,
                 drift=oe1_to_oe2,
                 f2=oe2_to_focus,
                 aperturex=oe1_aperturex,
                 aperturey=oe1_aperturey,
                 parameters=auto_parameters):
    srw_oe_array = []
    srw_pp_array = []

    oe_0 = SRWLOptA(_shape='r',
                    _ap_or_ob='a',
                    _Dx=aperturex,
                    _Dy=aperturey,
                    _x=0.0,
                    _y=0.0)

    pp_oe_0 = parameters[0]

    srw_oe_array.append(oe_0)
    srw_pp_array.append(pp_oe_0)

    oe_1 = SRWLOptL(_Fx=f1, _Fy=f1, _x=0.0, _y=0.0)

    pp_oe_1 =  parameters[1]

    srw_oe_array.append(oe_1)
    srw_pp_array.append(pp_oe_1)

    drift_before_oe_2 = SRWLOptD(drift)
    pp_drift_before_oe_2 =  parameters[2]

    srw_oe_array.append(drift_before_oe_2)
    srw_pp_array.append(pp_drift_before_oe_2)

    oe_3 = SRWLOptL(_Fx=f2, _Fy=f2, _x=0.0, _y=0.0)

    pp_oe_3 =  parameters[3]

    srw_oe_array.append(oe_3)
    srw_pp_array.append(pp_oe_3)

    drift_before_oe_4 = SRWLOptD(f2)
    pp_drift_before_oe_4 =  parameters[4]

    srw_oe_array.append(drift_before_oe_4)
    srw_pp_array.append(pp_drift_before_oe_4)

    return SRWLOptC(srw_oe_array, srw_pp_array)
