from core.ideal_optical_system import *
from scipy.constants import c

import matplotlib as mpl
mpl.rc('figure', max_open_warning = 0)

from silx.gui.plot import PlotWindow

def plot_data_files(outdir=None, plot_imaginary=False):

    outdir = os.path.join(base_output_dir, "time_domain") if outdir is None else outdir

    if not os.path.exists(outdir): return

    arReEt   = numpy.loadtxt(os.path.join(outdir, "Re_E_in_time_domain.txt"))
    arImEt   = numpy.loadtxt(os.path.join(outdir, "Im_E_in_time_domain.txt"))
    arAmpEt  = numpy.loadtxt(os.path.join(outdir, "Amp_E_in_time_domain.txt"))
    arPhiEt  = numpy.loadtxt(os.path.join(outdir, "Phi_E_in_time_domain.txt"))
    arPowt   = numpy.loadtxt(os.path.join(outdir, "Power_in_time_domain.txt"))
    arPowDt  = numpy.loadtxt(os.path.join(outdir, "Power_Density_in_time_domain.txt"))
    arPowDt2 = numpy.loadtxt(os.path.join(outdir, "Power_Density_2_in_time_domain.txt"))
    arIntf   = numpy.loadtxt(os.path.join(outdir, "Int_in_frequency_domain.txt"))

    plot_data(arReEt, arImEt, arAmpEt, arPhiEt, arPowt, arPowDt, arPowDt2, arIntf, plot_imaginary)

def plot_data(arReEt, arImEt, arAmpEt, arPhiEt, arPowt, arPowDt, arPowDt2, arIntf, plot_imaginary=False):
    def plot_array(ar, title, xlabel, ylabel):
        window = PlotWindow(fit=True)
        window.setGraphTitle(title)
        window.addCurve(ar[:, 0], ar[:, 1], xlabel=xlabel, ylabel=ylabel)
        window.show()

    if plot_imaginary:
        plot_array(arReEt, 'Real part of Electric Field in Time Domain', 'ct [\u03bcm]', 'Re(E) [V/mm]')
        plot_array(arImEt, 'Imaginary part of Electric Field in Time Domain', 'ct [\u03bcm]', 'Im(E) [V/mm]')

    plot_array(arAmpEt, 'Amplitude of Electric Field in Time Domain', 'ct [\u03bcm]', 'AmplitudeE) [V/mm]')
    plot_array(arPhiEt, 'Phase of Electric Field in Time Domain', 'ct [\u03bcm]', 'Phi(E) [radians]')
    plot_array(arPowt, 'Power in Time Domain', 'ct [\u03bcm]', 'Power [W]')
    plot_array(arPowDt, 'Power Density (On Axis) in Time Domain', 'ct [\u03bcm]', 'Power Density [W/mm^2]')
    plot_array(arPowDt2, '(Power Density/gamma^3) (On Axis) in Time Domain', 'ct [\u03bcm]', 'Power Density [W/mm^2]')
    plot_array(arIntf, 'Flux Density (On Axis) in Frequency Domain', 'E [eV]', 'Flux Density [ph/s/mm^2/.1%BW]')

from PyQt5.QtWidgets import QApplication
import sys

if __name__=="__main__":
    app = QApplication(sys.argv)

    try:
        plot_data_files(outdir=sys.argv[1], plot_imaginary=sys.argv[2]=="1")
    except:
        try:    plot_data_files(outdir=sys.argv[1])
        except: plot_data_files()

    app.exec_()
