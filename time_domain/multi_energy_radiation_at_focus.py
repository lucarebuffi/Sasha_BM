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

    wfrEXY_F = cp_deepcopy(wfrEXY)

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

    save_3D_wavefront(wfrEXY,   filename=WAVEFRONT_T_3D_FILE)
    save_3D_wavefront(wfrEXY_F, filename=WAVEFRONT_F_3D_FILE)

    return wfrEXY, wfrEXY_F

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

def extract_data_multi_electron_radiation_at_focus(wfrEXY_T, wfrEXY_F, show_data=True, save_data=True, plot_imaginary=False):
    mesh  = wfrEXY_T.mesh
    meshf = wfrEXY_F.mesh

    arReEt = array('f', [0] * mesh.ne)
    srwl.CalcIntFromElecField(arReEt, wfrEXY_T, 0, 5, 0, 0.0, 0.0, 0.0)

    arImEt = array('f', [0] * mesh.ne)
    srwl.CalcIntFromElecField(arImEt, wfrEXY_T, 0, 6, 0, 0.0, 0.0, 0.0)

    arPowt = array('f', [0] * mesh.ne)
    srwl.CalcIntFromElecField(arPowt, wfrEXY_T, 0, 2, 0, 0.0, 0.0, 0.0)

    arPowDt = array('f', [0] * mesh.ne)
    srwl.CalcIntFromElecField(arPowDt, wfrEXY_T, 0, 0, 0, 0.0, 0.0, 0.0)

    arAmpEt   = array('f', [0] * mesh.ne)
    arPhiEt   = array('f', [0] * mesh.ne)

    energy_step = (meshf.eFin - meshf.eStart)/meshf.ne

    for ie in range(mesh.ne):
        Et_ie = arReEt[ie] + 1.0j*arImEt[ie]

        arPhiEt[ie]   = numpy.angle(Et_ie)
        arAmpEt[ie]   = numpy.abs(Et_ie)
        arPowt[ie]    = arPowt[ie]  * codata.e * 1000 * (meshf.eStart + ie*energy_step)
        arPowDt[ie]   = arPowDt[ie] * codata.e * 1000 * (meshf.eStart + ie*energy_step)

    arIntf = array('f', [0] * wfrEXY_F.mesh.ne)
    srwl.CalcIntFromElecField(arIntf, wfrEXY_F, 6, 0, 0, meshf.eStart, 0, 0)

    if save_data: save_data_files(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, arIntf, meshf)
    if show_data: plot_data(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, arIntf, meshf, plot_imaginary)

def save_data_files(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, arIntf, meshf):
    outdir = os.path.join(base_output_dir, "time_domain")

    if not os.path.exists(outdir): os.mkdir(outdir)

    try:    srwl_uti_save_intens_ascii(arReEt, mesh, os.path.join(outdir, "Re_E_in_time_domain.dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arImEt, mesh, os.path.join(outdir, "Im_E_in_time_domain.dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arAmpEt, mesh, os.path.join(outdir, "Amp_E_in_time_domain.dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arPhiEt, mesh, os.path.join(outdir, "Phi_E_in_time_domain.dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arPowt, mesh, os.path.join(outdir, "Power_in_time_domain.dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arPowDt, mesh, os.path.join(outdir, "Power_Density_in_time_domain.dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arIntf, meshf, os.path.join(os.path.join(os.getcwd(), "output"), "Int_in_frequency_domain.dat"), 0)
    except: pass

    save_numpy_format(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, arIntf, meshf, outdir)

from scipy.constants import c

def save_numpy_format(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, arIntf, meshf, outdir):
    factor = c * 1e6  # to micron (c*t)

    def create_array(ar, mesh):
        np_array = numpy.zeros((mesh.ne, 2))
        np_array[:, 0] = numpy.linspace(mesh.eStart * factor, mesh.eFin * factor, mesh.ne)
        np_array[:, 1] = numpy.array(ar)

        return np_array

    numpy.savetxt(os.path.join(outdir, "Re_E_in_time_domain.txt"), create_array(arReEt, mesh))
    numpy.savetxt(os.path.join(outdir, "Im_E_in_time_domain.txt"), create_array(arImEt, mesh))
    numpy.savetxt(os.path.join(outdir, "Amp_E_in_time_domain.txt"), create_array(arAmpEt, mesh))
    numpy.savetxt(os.path.join(outdir, "Phi_E_in_time_domain.txt"), create_array(arPhiEt, mesh))
    numpy.savetxt(os.path.join(outdir, "Power_in_time_domain.txt"), create_array(arPowt, mesh))
    numpy.savetxt(os.path.join(outdir, "Power_Density_in_time_domain.txt"), create_array(arPowDt, mesh))
    numpy.savetxt(os.path.join(outdir, "Int_in_frequency_domain.txt"), create_array(arIntf, meshf))

import sys

if __name__=="__main__":
    if not srwl_uti_proc_is_master(): exit()

    try:    load_existing = int(sys.argv[1]) == 1
    except: load_existing = False

    try:    ne = int(sys.argv[2])
    except: ne = spectrum_energy_ne

    t0 = time.time()

    if not load_existing:
        print("Calculating 3D E-field on " + str(ne) + " energy points, in the range [" + str(spectrum_energy_from) + ", " + str(spectrum_energy_to) + "]")
        wfrEXY = calculate_initial_multi_energy_radiation(get_electron_beam(),
                                                          get_magnetic_field_container(magnetic_field_file_name),
                                                          energy_from=spectrum_energy_from,
                                                          energy_to=spectrum_energy_to,
                                                          ne=ne)
        print("done in", round(time.time()-t0, 3))

        wfrEXY_T, wfrEXY_F = calculate_multi_energy_radiation_at_focus(wfrEXY, get_beamline(), resize=True, t0=t0)
    else:
        wfrEXY_T = load_3D_wavefront(t0=t0, filename=WAVEFRONT_T_3D_FILE)
        wfrEXY_F = load_3D_wavefront(t0=time.time(), filename=WAVEFRONT_F_3D_FILE)

    extract_data_multi_electron_radiation_at_focus(wfrEXY_T, wfrEXY_F)
