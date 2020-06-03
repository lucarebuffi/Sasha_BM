import os, numpy
from matplotlib import pyplot as plt
from silx.gui.plot import Plot2D
from core.default_values import base_output_dir

def plot_spectrum(spectrum):
    plt.plot(spectrum[:, 0], spectrum[:, 1])
    plt.xlabel("Energy [eV]")
    plt.ylabel("Spectral Flux [ph/s/0.1%BW]")
    plt.title("Spectrum used for Power Calculation")
    plt.show()

def plot_power_density(x_coord, y_coord, power_density):
    origin = (x_coord[0], y_coord[0])
    scale = (x_coord[1] - x_coord[0], y_coord[1] - y_coord[0])
    area = scale[0]*scale[1]

    data_to_plot = power_density.T

    colormap = {"name": "temperature", "normalization": "linear", "autoscale": True, "vmin": 0, "vmax": 0, "colors": 256}

    plot_canvas = Plot2D()

    plot_canvas.resetZoom()
    plot_canvas.setXAxisAutoScale(True)
    plot_canvas.setYAxisAutoScale(True)
    plot_canvas.setGraphGrid(False)
    plot_canvas.setKeepDataAspectRatio(True)
    plot_canvas.yAxisInvertedAction.setVisible(False)

    plot_canvas.setXAxisLogarithmic(False)
    plot_canvas.setYAxisLogarithmic(False)
    plot_canvas.getMaskAction().setVisible(False)
    plot_canvas.getRoiAction().setVisible(False)
    plot_canvas.getColormapAction().setVisible(True)
    plot_canvas.setKeepDataAspectRatio(False)

    plot_canvas.addImage(numpy.array(data_to_plot),
                         legend="Power Density",
                         scale=scale,
                         origin=origin,
                         colormap=colormap,
                         replace=True)

    plot_canvas.setActiveImage("Power Density")
    plot_canvas.setGraphXLabel("Horizontal Position [mm]")
    plot_canvas.setGraphYLabel("Vertical Position [mm]")
    plot_canvas.setGraphTitle("Power Density [nW/mm^2]\nTotal Power = " + str(round(power_density.sum()*area, 6)) + " nW")

    plot_canvas.show()

def plot_data_files(outdir=None):
    outdir = os.path.join(base_output_dir, "frequency_domain") if outdir is None else outdir
    if not os.path.exists(outdir): return

    spectrum            = numpy.loadtxt(os.path.join(outdir, "Spectrum_at_focus.txt"))
    plot_coordinates_x  = numpy.loadtxt(os.path.join(outdir, "Power_Density_at_Focus_coord_x.txt"))
    plot_coordinates_y  = numpy.loadtxt(os.path.join(outdir, "Power_Density_at_Focus_coord_y.txt"))
    total_power_density = numpy.loadtxt(os.path.join(outdir, "Power_Density_at_Focus.txt"))

    plot_spectrum(spectrum)
    plot_power_density(plot_coordinates_x, plot_coordinates_y, total_power_density)


from PyQt5.QtWidgets import QApplication
import sys

if __name__=="__main__":
    app = QApplication(sys.argv)

    try:    plot_data_files(outdir=sys.argv[1])
    except: plot_data_files()

    app.exec_()
