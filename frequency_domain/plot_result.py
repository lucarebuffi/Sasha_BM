import numpy

from silx.gui.plot import Plot2D

def plot_power_density(x_coord, y_coord, power_density):
    x_coord *= 1000
    y_coord *= 1000

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
    plot_canvas.setGraphTitle("Power Density - Total Power = " + str(power_density.sum()*area) + " W")

    plot_canvas.show()
