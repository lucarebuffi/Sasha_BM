from lib.default_values import magnetic_field_file_name_input, magnetic_field_file_name
import numpy

if __name__ == "__main__":

    data = numpy.loadtxt(magnetic_field_file_name_input, skiprows=1)

    from matplotlib import pyplot as plt

    plt.plot(data[:, 0], data[:, 1])
    plt.title("Magnetic Field from file: " + magnetic_field_file_name_input)
    plt.xlabel("Z [cm]")
    plt.ylabel("By [Gauss]")
    plt.show()

    data[:, 0] *= 1e-2 # to meters
    data[:, 1] *= 1e-4 # to Tesla

    numpy.savetxt(magnetic_field_file_name_input + ".out", data) # for Shadow use

    text = "#Bx [T], By [T], Bz [T] on 3D mesh: inmost loop vs X (horizontal transverse position), outmost loop vs Z (longitudinal position)\n" + \
           "#0.0 #initial X position [m]\n" + \
           "#0.0 #step of X [m]\n" + \
           "#1 #number of points vs X\n" + \
           "#0.0 #initial Y position [m]\n" + \
           "#0.0 #step of Y [m]\n" + \
           "#1 #number of points vs Y\n" + \
           "#" + str(data[0, 0]) + " #initial Z position [m]\n" + \
           "#" + str(round(data[1, 0]-data[0, 0], 6)) + " #step of Z [m]\n" + \
           "#" + str(data.shape[0]) + "#number of points vs Z\n"

    for i in range(data.shape[0]):
        text += "0.0\t" + str(round(data[i, 1], 8)) + "\t0.0\n"
    text = text[:-1]

    f = open(magnetic_field_file_name, "w")
    f.write(text)
    f.close()

    print("file " + magnetic_field_file_name + " created")
