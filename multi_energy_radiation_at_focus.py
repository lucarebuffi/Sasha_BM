import pickle

from lib.default_values import gamma
from lib.electron_beam import get_electron_beam
from lib.magnetic_structure import get_magnetic_field_container
from lib.ideal_optical_system import *

from multi_energy_radiation_from_source import calculate_initial_multi_energy_radiation
from plot_results import plot_data

def calculate_multi_energy_radiation_at_focus(wfrEXY, optBL, resize=False, t0=time.time()):
     # 3D Freq. dependent
    print("Propagating 3D E-field")
    srwl.PropagElecField(wfrEXY, optBL)
    print("done in", round(time.time()-t0, 3))

    print("Resizing in Frequency domain")
    t0 = time.time()
    srwl.ResizeElecField(wfrEXY, "f", [0, 2, 1])
    print("done in", round(time.time()-t0, 3))

    print("Switching to Time domain")
    t0 = time.time()
    srwl.SetRepresElecField(wfrEXY, "t",)
    print("done in", round(time.time()-t0, 3))

    if resize:
        print("Resizing in Time domain")
        t0 = time.time()
        srwl.ResizeElecField(wfrEXY, "t", [0, 0.5, 1])
        print("done in", round(time.time()-t0, 3))

    save_3D_wavefront(wfrEXY)

    return wfrEXY


def save_3D_wavefront(wfrEXY):
    outdir = os.path.join(os.getcwd(), "output")

    if not os.path.exists(outdir): os.mkdir(outdir)
    print('   Saving wavefront data to a file ... ', end='')
    t0 = time.time()
    try:
        output_file = open(os.path.join(outdir, "3D_Propagated_Waferont.dat"), 'wb')
        pickle.dump(wfrEXY, output_file)
        output_file.flush()
        output_file.close()
        print('done in', round(time.time() - t0), 's')
    except:
        try:    os.remove(output_file)
        except: pass

        print("Wavefront not saved")

def load_3D_wavefront(t0):
    outdir = os.path.join(os.getcwd(), "output")

    print('   Loading wavefront data from a file ... ', end='')

    input_file = open(os.path.join(outdir, "3D_Propagated_Waferont.dat"), 'rb')
    wfrEXY = pickle.load(input_file)
    input_file.close()

    print('done in', round(time.time() - t0), 's')

    return wfrEXY

def extract_data_multi_electron_radiation_at_focus(wfrEXY, show_data=True, save_data=True, plot_imaginary=False):
    mesh = wfrEXY.mesh

    arReEt = array('f', [0] * mesh.ne)
    srwl.CalcIntFromElecField(arReEt, wfrEXY, 0, 5, 0, 0.0, 0.0, 0.0)

    arImEt = array('f', [0] * mesh.ne)
    srwl.CalcIntFromElecField(arImEt, wfrEXY, 0, 6, 0, 0.0, 0.0, 0.0)

    arPowt = array('f', [0] * mesh.ne)
    srwl.CalcIntFromElecField(arPowt, wfrEXY, 0, 2, 0, 0.0, 0.0, 0.0)

    arPowDt = array('f', [0] * mesh.ne)
    srwl.CalcIntFromElecField(arPowDt, wfrEXY, 0, 0, 0, 0.0, 0.0, 0.0)

    arAmpEt  = array('f', [0] * mesh.ne)
    arPhiEt  = array('f', [0] * mesh.ne)

    power_factor = 1/gamma**3

    for ie in range(mesh.ne):
        Et_ie = arReEt[ie] + 1.0j*arImEt[ie]

        arPhiEt[ie]  = numpy.angle(Et_ie)
        arAmpEt[ie]  = numpy.abs(Et_ie)

        arPowt[ie]  *= power_factor
        arPowDt[ie] *= power_factor

    if save_data: save_data_files(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, wfrEXY)
    if show_data: plot_data(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, plot_imaginary)

def save_data_files(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, wfrEXY):
    outdir = os.path.join(os.getcwd(), "output")

    if not os.path.exists(outdir): os.mkdir(outdir)

    try:    srwl_uti_save_intens_ascii(arReEt, wfrEXY.mesh, os.path.join(outdir, "Re_E_in_time_domain.dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arImEt, wfrEXY.mesh, os.path.join(outdir, "Im_E_in_time_domain.dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arAmpEt, wfrEXY.mesh, os.path.join(outdir, "Amp_E_in_time_domain.dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arPhiEt, wfrEXY.mesh, os.path.join(outdir, "Phi_E_in_time_domain.dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arPowt, wfrEXY.mesh, os.path.join(outdir, "Power_in_time_domain.dat"), 0)
    except: pass

    try:    srwl_uti_save_intens_ascii(arPowDt, wfrEXY.mesh, os.path.join(outdir, "Power_Density_in_time_domain.dat"), 0)
    except: pass

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

        wfrEXY = calculate_multi_energy_radiation_at_focus(wfrEXY, get_beamline(), resize=True, t0=t0)
    else:
        wfrEXY = load_3D_wavefront(t0=t0)

    extract_data_multi_electron_radiation_at_focus(wfrEXY)
