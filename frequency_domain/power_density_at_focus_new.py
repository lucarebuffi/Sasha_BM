import numpy
from core.electron_beam import get_electron_beam
from core.magnetic_structure import get_magnetic_field_container
from core.ideal_optical_system import *
from core.default_values import magnetic_field_file_name

from frequency_domain.single_energy_radiation_from_source import calculate_initial_single_energy_radiation
from frequency_domain.single_energy_radiation_at_focus import calculate_single_energy_radiation_at_focus
from frequency_domain.plot_results import plot_power_density, plot_spectrum

def get_wavefront_data(wfr, polarization=6):
    dim_x = wfr.mesh.nx
    dim_y = wfr.mesh.ny

    arI = array('f', [0] * wfr.mesh.nx * wfr.mesh.ny)
    arReE = array('f', [0] * wfr.mesh.nx * wfr.mesh.ny)
    arImE = array('f', [0] * wfr.mesh.nx * wfr.mesh.ny)

    srwl.CalcIntFromElecField(arI,   wfr, polarization, 0, 3, wfr.mesh.eStart, 0, 0)
    srwl.CalcIntFromElecField(arReE, wfr, polarization, 5, 3, wfr.mesh.eStart, 0, 0)
    srwl.CalcIntFromElecField(arImE, wfr, polarization, 6, 3, wfr.mesh.eStart, 0, 0)

    # um in mm
    return numpy.array(arI).reshape((dim_y, dim_x)).T, \
           numpy.array(arReE).reshape((dim_y, dim_x)).T,\
           numpy.array(arImE).reshape((dim_y, dim_x)).T

from scipy.interpolate import RectBivariateSpline
from PyQt5.QtWidgets import QApplication
import sys

def run_script(argv):
    if not srwl_uti_proc_is_master(): exit()

    if len(argv) == 3:
        e_in  = float(argv[0])
        e_fin = float(argv[1])
        n_e   = int(argv[2])
    else:
        e_in  = 0.1
        e_fin = 200.1
        n_e   = 201

    app = QApplication([])

    energies      = numpy.linspace(e_in, e_fin, n_e)
    delta_energy  = energies[1] - energies[0]
    electron_beam = get_electron_beam(x0=-2e-6)
    magnetic_field_container = get_magnetic_field_container(magnetic_field_file_name)

    dim_x = 1001
    dim_y = 1001

    # um in mm
    plot_coordinates_x = numpy.linspace(-0.1, 0.1, dim_x)
    plot_coordinates_y = numpy.linspace(-0.1, 0.1, dim_y)

    spectrum            = numpy.zeros((n_e, 2))
    spectrum[:, 0]      = energies

    source_parameters      = default_source_parameters
    propagation_parameters = auto_parameters

    total_re = None
    total_im = None

    for energy, ie in zip(energies, range(n_e)):
        wfr = calculate_initial_single_energy_radiation(electron_beam, magnetic_field_container, energy=energy, source_parameters=source_parameters)
        wfr = calculate_single_energy_radiation_at_focus(wfr, get_beamline(parameters=propagation_parameters))

        x_coord    = numpy.linspace(wfr.mesh.xStart, wfr.mesh.xFin, wfr.mesh.nx) * 1000 # mm
        y_coord    = numpy.linspace(wfr.mesh.yStart, wfr.mesh.yFin, wfr.mesh.ny) * 1000 # mm
        pixel_area = (x_coord[1] - x_coord[0]) * (y_coord[1] - y_coord[0])              # mm^2

        intensity, re_field, im_field = get_wavefront_data(wfr)                   # photons/s/mm^2/0.1%BW
        intensity[numpy.where(numpy.isnan(intensity))] = 0.0
        re_field[numpy.where(numpy.isnan(re_field))] = 0.0
        im_field[numpy.where(numpy.isnan(im_field))] = 0.0

        integrated_flux = intensity.sum() * pixel_area         # photons/s/0.1%BW

        spectrum[ie, 1]   = integrated_flux

        re_field_de = re_field * numpy.sqrt(1e3 * delta_energy / energy)
        im_field_de = im_field * numpy.sqrt(1e3 * delta_energy / energy)

        # to cumulate we need the same spatial mesh
        interpolator  = RectBivariateSpline(x_coord, y_coord, re_field_de)
        re_field_de = interpolator(plot_coordinates_x, plot_coordinates_y)
        re_field_de[numpy.where(numpy.isnan(re_field))] = 0.0

        interpolator  = RectBivariateSpline(x_coord, y_coord, im_field_de)
        im_field_de = interpolator(plot_coordinates_x, plot_coordinates_y)
        im_field_de[numpy.where(numpy.isnan(im_field))] = 0.0

        if total_re is None: total_re = re_field
        else: total_re += re_field

        if total_im is None: total_im = im_field
        else: total_im += im_field

        print("Energy", round(energy, 2), ", S.F.", round(integrated_flux, 2), "ph/s/0.1%BW")

    total_amplitude = numpy.abs(total_re + 1j*total_im)
    total_intensity = total_amplitude**2

    total_power_density = (total_intensity * codata.e * delta_energy ) * 1e9     # nW/mm^2
    power               = total_power_density.sum() *  (plot_coordinates_x[1] - plot_coordinates_x[0]) * (plot_coordinates_y[1] - plot_coordinates_y[0]) # power in nW in the interval E + dE

    print("Total Power", power, "nW")

    # cumulative quantities ##################################


    outdir = os.path.join(base_output_dir, "frequency_domain")
    if not os.path.exists(outdir): os.mkdir(outdir)

    numpy.savetxt(os.path.join(outdir, "Spectrum_at_focus.txt"),                       spectrum)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus_coord_x.txt"), plot_coordinates_x)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus_coord_y.txt"), plot_coordinates_y)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus.txt"),         total_power_density)

    plot_spectrum(spectrum)
    plot_power_density(plot_coordinates_x, plot_coordinates_y, total_power_density)

    app.exec_()

if __name__=="__main__":
    run_script(sys.argv[1:])
