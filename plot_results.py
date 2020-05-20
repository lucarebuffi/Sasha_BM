from lib.default_values import gamma
from lib.ideal_optical_system import *
from scipy.constants import c

import matplotlib as mpl
mpl.rc('figure', max_open_warning = 0)

def plot_data_files(outdir=None, plot_imaginary=False):

    outdir = os.path.join(os.getcwd(), "output") if outdir is None else outdir

    if not os.path.exists(outdir): return

    arReEt, mesh = srwl_uti_read_intens_ascii(os.path.join(outdir, "Re_E_in_time_domain.dat"))
    arImEt, _    = srwl_uti_read_intens_ascii(os.path.join(outdir, "Im_E_in_time_domain.dat"))
    arAmpEt, _   = srwl_uti_read_intens_ascii(os.path.join(outdir, "Amp_E_in_time_domain.dat"))
    arPhiEt, _   = srwl_uti_read_intens_ascii(os.path.join(outdir, "Phi_E_in_time_domain.dat"))
    arPowt, _    = srwl_uti_read_intens_ascii(os.path.join(outdir, "Power_in_time_domain.dat"))
    arPowDt, _   = srwl_uti_read_intens_ascii(os.path.join(outdir, "Power_Density_in_time_domain.dat"))

    save_numpy_format(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, outdir)

    plot_data(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, plot_imaginary)

def save_numpy_format(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, outdir):
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

def plot_data(arAmpEt, arPhiEt, arPowDt, arPowt, arReEt, arImEt, mesh, plot_imaginary=False):
    factor = c * 1e6  # to micron (c*t)

    plot_range = [mesh.eStart * factor, mesh.eFin * factor, mesh.ne]

    if plot_imaginary:
        uti_plot1d(arReEt, plot_range,
                   labels=['ct', 'Re(E)', 'Real part of Electric Field in Time Domain'],
                   units=['\u03bcm', 'V/mm'])

        uti_plot1d(arImEt, plot_range,
                   labels=['ct', 'Im(E)', 'Imaginary part of Electric Field in Time Domain'],
                   units=['\u03bcm', 'V/mm'])

    uti_plot1d(arAmpEt, plot_range,
               labels=['ct', 'Amplitude(E)', 'Amplitude of Electric Field in Time Domain'],
               units=['\u03bcm', 'V/mm'])

    uti_plot1d(arPhiEt, plot_range,
               labels=['ct', 'Phi(E)', 'Phase Electric Field in Time Domain'],
               units=['\u03bcm', 'radians'])

    uti_plot1d(arPowt, plot_range,
               labels=['ct', 'Power', 'Power in Time Domain'],
               units=['\u03bcm', 'W'])

    uti_plot1d(arPowDt, plot_range,
               labels=['ct', 'Power Density', 'Power Density (On Axis) in Time Domain'],
               units=['\u03bcm', 'W/mm^2'])

    uti_plot_show()


if __name__=="__main__":
    if not srwl_uti_proc_is_master(): exit()

    try:
        plot_data_files(outdir=os.path.join(os.getcwd(), sys.argv[1]), plot_imaginary=sys.argv[2]=="1")
    except:
        try:    plot_data_files(outdir=os.path.join(os.getcwd(), sys.argv[1]))
        except: plot_data_files()
