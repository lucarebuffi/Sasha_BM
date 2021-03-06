from core.electron_beam import get_electron_beam
from core.magnetic_structure import get_magnetic_field_container
from core.ideal_optical_system import *
from core.default_values import magnetic_field_file_name

from frequency_domain.single_energy_radiation_from_source import calculate_initial_single_energy_radiation, plot_single_energy_radiation

def calculate_single_energy_radiation_at_focus(wfr, optBL):
    srwl.PropagElecField(wfr, optBL)
    return wfr

if __name__=="__main__":
    if not srwl_uti_proc_is_master(): exit()

    try:    energy = float(sys.argv[1])
    except: energy = 20

    try:    shiftx = float(sys.argv[2])
    except: shiftx = 0.0

    wfr = calculate_initial_single_energy_radiation(get_electron_beam(x0=-2e-6),
                                                    get_magnetic_field_container(magnetic_field_file_name),
                                                    energy=energy,
                                                    source_parameters=default_source_parameters,
                                                    shiftx=shiftx,
                                                    aperturex=0.015,
                                                    aperturey=0.015)

    plot_single_energy_radiation(wfr, where="Before", show=False)

    wfr = calculate_single_energy_radiation_at_focus(wfr, get_beamline())

    plot_single_energy_radiation(wfr, where="After", show=True)
