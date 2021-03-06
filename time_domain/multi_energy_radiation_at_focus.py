import pickle
from copy import deepcopy as cp_deepcopy

from core.electron_beam import get_electron_beam
from core.magnetic_structure import get_magnetic_field_container
from core.ideal_optical_system import *

from time_domain.multi_energy_radiation_from_source import calculate_initial_multi_energy_radiation
from time_domain.plot_results import plot_data

import scipy.constants as codata

WAVEFRONT_T_3D_FILE = "3D_Propagated_Wavefront_T.dat"
WAVEFRONT_F_3D_FILE = "3D_Propagated_Wavefront_F.dat"

def calculate_multi_energy_radiation_at_focus(wfrEXY, optBL, resize=False, t0=time.time()):
     # 3D Freq. dependent
    print("Propagating 3D E-field")
    srwl.PropagElecField(wfrEXY, optBL)
    print("done in", round(time.time()-t0, 3), "s")

    # for time domain calculations
    print("Resizing in Frequency domain")
    t0 = time.time()
    srwl.ResizeElecField(wfrEXY, "f", [0, 2, 1])
    print("done in", round(time.time()-t0, 3), "s")

    print("Switching to Time domain")
    t0 = time.time()
    srwl.SetRepresElecField(wfrEXY, "t",)

    print("done in", round(time.time()-t0, 3), "s")

    if resize:
        print("Resizing in Time domain")
        t0 = time.time()
        srwl.ResizeElecField(wfrEXY, "t", [0, 0.5, 1])
        print("done in", round(time.time()-t0, 3), "s")

    save_3D_wavefront(wfrEXY, filename=WAVEFRONT_T_3D_FILE)

    return wfrEXY

def save_3D_wavefront(wfrEXY, filename):
    outdir = os.path.join(base_output_dir, "time_domain")

    if not os.path.exists(outdir): os.mkdir(outdir)
    print('   Saving wavefront data to a file ... ', end='')
    t0 = time.time()
    try:
        output_file = open(os.path.join(outdir, filename), 'wb')
        pickle.dump(wfrEXY, output_file)
        output_file.flush()
        output_file.close()
        print('done in', round(time.time() - t0), 's')
    except:
        try:    os.remove(output_file)
        except: pass

        print("Wavefront not saved")

def load_3D_wavefront(t0, filename):
    outdir = os.path.join(base_output_dir, "time_domain")

    print('   Loading wavefront data from a file ... ', end='')

    input_file = open(os.path.join(outdir, filename), 'rb')
    wfrEXY = pickle.load(input_file)
    input_file.close()

    print('done in', round(time.time() - t0), 's')

    return wfrEXY

def extract_data_multi_electron_radiation_at_focus(wfrEXY_T, show_data=True, save_data=True, plot_imaginary=False, polarization="s"):
    if polarization == "s": param_pol = 0
    elif polarization == "p": param_pol = 1
    else: param_pol = 6

    mesh  = wfrEXY_T.mesh

    arReEt = array('f', [0] * mesh.ne)
    srwl.CalcIntFromElecField(arReEt, wfrEXY_T, param_pol, 5, 0, 0.0, 0.0, 0.0)

    arImEt = array('f', [0] * mesh.ne)
    srwl.CalcIntFromElecField(arImEt, wfrEXY_T, param_pol, 6, 0, 0.0, 0.0, 0.0)

    arPowt = array('f', [0] * mesh.ne)
    srwl.CalcIntFromElecField(arPowt, wfrEXY_T, param_pol, 2, 0, 0.0, 0.0, 0.0)

    arPowDt = array('f', [0] * mesh.ne)
    srwl.CalcIntFromElecField(arPowDt, wfrEXY_T, param_pol, 0, 0, 0.0, 0.0, 0.0)

    arAmpEt   = array('f', [0] * mesh.ne)
    arPhiEt   = array('f', [0] * mesh.ne)

    for ie in range(mesh.ne):
        Et_ie = arReEt[ie] + 1.0j*arImEt[ie]

        arPhiEt[ie]   = numpy.angle(Et_ie)
        arAmpEt[ie]   = numpy.abs(Et_ie)

    if save_data: save_data_files(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, polarization)
    if show_data: plot_data(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, plot_imaginary, polarization)

def save_data_files(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, polarization):
    outdir = os.path.join(base_output_dir, "time_domain")

    if not os.path.exists(outdir): os.mkdir(outdir)

    try:    srwl_uti_save_intens_ascii(arReEt, mesh, os.path.join(outdir, "Re_E_in_time_domain_" + polarization + ".dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arImEt, mesh, os.path.join(outdir, "Im_E_in_time_domain_" + polarization + ".dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arAmpEt, mesh, os.path.join(outdir, "Amp_E_in_time_domain_" + polarization + ".dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arPhiEt, mesh, os.path.join(outdir, "Phi_E_in_time_domain_" + polarization + ".dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arPowt, mesh, os.path.join(outdir, "Power_in_time_domain_" + polarization + ".dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arPowDt, mesh, os.path.join(outdir, "Power_Density_in_time_domain_" + polarization + ".dat"), 0)
    except: pass

    save_numpy_format(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, outdir, polarization)

from scipy.constants import c

def save_numpy_format(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, outdir, polarization):
    factor = c * 1e6  # to micron (c*t)

    def create_array(ar, mesh):
        np_array = numpy.zeros((mesh.ne, 2))
        np_array[:, 0] = numpy.linspace(mesh.eStart * factor, mesh.eFin * factor, mesh.ne)
        np_array[:, 1] = numpy.array(ar)

        return np_array

    numpy.savetxt(os.path.join(outdir, "Re_E_in_time_domain_" + polarization + ".txt"), create_array(arReEt, mesh))
    numpy.savetxt(os.path.join(outdir, "Im_E_in_time_domain_" + polarization + ".txt"), create_array(arImEt, mesh))
    numpy.savetxt(os.path.join(outdir, "Amp_E_in_time_domain_" + polarization + ".txt"), create_array(arAmpEt, mesh))
    numpy.savetxt(os.path.join(outdir, "Phi_E_in_time_domain_" + polarization + ".txt"), create_array(arPhiEt, mesh))
    numpy.savetxt(os.path.join(outdir, "Power_in_time_domain_" + polarization + ".txt"), create_array(arPowt, mesh))
    numpy.savetxt(os.path.join(outdir, "Power_Density_in_time_domain_" + polarization + ".txt"), create_array(arPowDt, mesh))

import sys


def run_script(argv):
    if not srwl_uti_proc_is_master(): exit()

    try:    load_existing = int(argv[0]) == 1
    except: load_existing = False

    try:    ne = int(argv[1])
    except: ne = spectrum_energy_ne

    try:    do_propagation = int(argv[2]) == 1
    except: do_propagation = True

    t0 = time.time()

    if not load_existing:
        print("Calculating 3D E-field on " + str(ne) + " energy points, in the range [" + str(spectrum_energy_from) + ", " + str(spectrum_energy_to) + "]")
        wfrEXY = calculate_initial_multi_energy_radiation(get_electron_beam(x0=-2e-6),
                                                          get_magnetic_field_container(magnetic_field_file_name),
                                                          energy_from=spectrum_energy_from,
                                                          energy_to=spectrum_energy_to,
                                                          ne=ne,
                                                          aperturex=0.015,
                                                          aperturey=0.015)
        print("done in", round(time.time()-t0, 3))

        print("Check values", max(wfrEXY.arEx), max(wfrEXY.arEy))

        if do_propagation:
            wfrEXY_T  = calculate_multi_energy_radiation_at_focus(wfrEXY, get_beamline(), resize=False, t0=t0)

            extract_data_multi_electron_radiation_at_focus(wfrEXY_T, polarization="s")
            extract_data_multi_electron_radiation_at_focus(wfrEXY_T, polarization="p")
    else:
        wfrEXY_T = load_3D_wavefront(t0=t0, filename=WAVEFRONT_T_3D_FILE)

        extract_data_multi_electron_radiation_at_focus(wfrEXY_T, polarization="s")
        extract_data_multi_electron_radiation_at_focus(wfrEXY_T, polarization="p")

if __name__=="__main__":
    run_script(sys.argv[1:])
