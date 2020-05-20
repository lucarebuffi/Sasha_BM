from lib.ideal_optical_system import *
from scipy.constants import c

import matplotlib as mpl
mpl.rc('figure', max_open_warning = 0)

from silx.gui.plot import PlotWindow

def plot_data_files(outdir=None, plot_imaginary=False):

    outdir = os.path.join(os.getcwd(), "output") if outdir is None else outdir

    if not os.path.exists(outdir): return

    arReEt = numpy.loadtxt(os.path.join(outdir, "Re_E_in_time_domain.txt"))
    arImEt = numpy.loadtxt(os.path.join(outdir, "Im_E_in_time_domain.txt"))
    arAmpEt = numpy.loadtxt(os.path.join(outdir, "Amp_E_in_time_domain.txt"))
    arPhiEt = numpy.loadtxt(os.path.join(outdir, "Phi_E_in_time_domain.txt"))
    arPowt = numpy.loadtxt(os.path.join(outdir, "Power_in_time_domain.txt"))
    arPowDt = numpy.loadtxt(os.path.join(outdir, "Power_Density_in_time_domain.txt"))

    plot_data(arReEt, arImEt, arAmpEt, arPhiEt, arPowt, arPowDt, plot_imaginary)

def plot_data(arReEt, arImEt, arAmpEt, arPhiEt, arPowt, arPowDt, plot_imaginary=False):
    if plot_imaginary:
        window = PlotWindow()
        window.setGraphTitle('Real part of Electric Field in Time Domain')
        window.addCurve(arReEt[:, 0], arReEt[:, 1], xlabel='ct [\u03bcm]', ylabel='Re(E) [V/mm]')
        window.show()

        window = PlotWindow()
        window.setGraphTitle('Imaginary part of Electric Field in Time Domain')
        window.addCurve(arImEt[:, 0], arImEt[:, 1], xlabel='ct [\u03bcm]', ylabel='Im(E) [V/mm]')
        window.show()

    window = PlotWindow(fit=True)
    window.setGraphTitle('Amplitude of Electric Field in Time Domain')
    window.addCurve(arAmpEt[:, 0], arAmpEt[:, 1], xlabel='ct [\u03bcm]', ylabel='Amplitude(E) [V/mm]')
    window.show()

    window = PlotWindow()
    window.setGraphTitle('Phase of Electric Field in Time Domain')
    window.addCurve(arPhiEt[:, 0], arPhiEt[:, 1], xlabel='ct [\u03bcm]', ylabel='Phi(E) [radians]')
    window.show()

    window = PlotWindow(fit=True)
    window.setGraphTitle('Power in Time Domain')
    window.addCurve(arPowt[:, 0], arPowt[:, 1], xlabel='ct [\u03bcm]', ylabel='Power [W]')
    window.show()

    window = PlotWindow(fit=True)
    window.setGraphTitle('Power Density (On Axis) in Time Domain')
    window.addCurve(arPowDt[:, 0], arPowDt[:, 1], xlabel='ct [\u03bcm]', ylabel='Power Density [W/mm^2]')
    window.show()

from PyQt5.QtWidgets import QApplication
import sys

if __name__=="__main__":
    app = QApplication(sys.argv)

    try:
        plot_data_files(outdir=os.path.join(os.getcwd(), sys.argv[1]), plot_imaginary=sys.argv[2]=="1")
    except:
        try:    plot_data_files(outdir=os.path.join(os.getcwd(), sys.argv[1]))
        except: plot_data_files()

    app.exec_()
