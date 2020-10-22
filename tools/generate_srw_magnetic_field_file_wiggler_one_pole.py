
import numpy

if __name__ == "__main__":
    magnetic_field_file_name_input    = "/Users/lrebuffi/Box Sync/Luca_Xianbo_Share/Sasha/BM/data/wiggler.dat"
    magnetic_field_file_name          = "/Users/lrebuffi/Box Sync/Luca_Xianbo_Share/Sasha/BM/data/wiggler_srw.dat"
    magnetic_field_file_name_one_pole = "/Users/lrebuffi/Box Sync/Luca_Xianbo_Share/Sasha/BM/data/wiggler_1pole_srw.dat"

    data = numpy.loadtxt(magnetic_field_file_name_input, skiprows=0)

    from matplotlib import pyplot as plt

    plt.plot(data[:, 0], data[:, 1])
    plt.title("Magnetic Field from file: " + magnetic_field_file_name_input)
    plt.xlabel("Z [cm]")
    plt.ylabel("By [Gauss]")
    plt.show()

    data[:, 0] *= 1e-2 # to meters
    data[:, 1] *= 1e-4 # to Tesla

    data_1p_x = data[:281, 0] - data[280, 0]
    data_1p_x = numpy.append(data_1p_x, data[761:, 0] - data[760, 0])
    data_1p_y = data[:281, 1]
    data_1p_y = numpy.append(data_1p_y, data[761:, 1])

    data_1p = numpy.zeros((len(data_1p_x), 2))
    data_1p[:, 0] = data_1p_x[:]
    data_1p[:, 1] = data_1p_y[:]

    plt.plot(data_1p[:, 0], data_1p[:, 1])
    plt.title("1 pole Magnetic Field from file")
    plt.xlabel("Z [cm]")
    plt.ylabel("By [Gauss]")
    plt.show()

    numpy.savetxt(magnetic_field_file_name_input + ".out", data) # for Shadow use
    numpy.savetxt(magnetic_field_file_name_input + "_1pole_.out", data) # for Shadow use

    text = "#Bx [T], By [T], Bz [T] on 3D mesh: inmost loop vs X (horizontal transverse position), outmost loop vs Z (longitudinal position)\n" + \
           "#0.0 #initial X position [m]\n" + \
           "#0.0 #step of X [m]\n" + \
           "#1 #number of points vs X\n" + \
           "#0.0 #initial Y position [m]\n" + \
           "#0.0 #step of Y [m]\n" + \
           "#1 #number of points vs Y\n" + \
           "#" + str(data[0, 0]) + " #initial Z position [m]\n" + \
           "#" + str(round(data[1, 0]-data[0, 0], 6)) + " #step of Z [m]\n" + \
           "#" + str(data.shape[0]) + " #number of points vs Z\n"

    for i in range(data.shape[0]):
        text += "0.0\t" + str(round(data[i, 1], 8)) + "\t0.0\n"
    text = text[:-1]

    f = open(magnetic_field_file_name, "w")
    f.write(text)
    f.close()

    print("file " + magnetic_field_file_name + " created")

    text = "#Bx [T], By [T], Bz [T] on 3D mesh: inmost loop vs X (horizontal transverse position), outmost loop vs Z (longitudinal position)\n" + \
           "#0.0 #initial X position [m]\n" + \
           "#0.0 #step of X [m]\n" + \
           "#1 #number of points vs X\n" + \
           "#0.0 #initial Y position [m]\n" + \
           "#0.0 #step of Y [m]\n" + \
           "#1 #number of points vs Y\n" + \
           "#" + str(data_1p[0, 0]) + " #initial Z position [m]\n" + \
           "#" + str(round(data_1p[1, 0]-data_1p[0, 0], 6)) + " #step of Z [m]\n" + \
           "#" + str(data_1p.shape[0]) + " #number of points vs Z\n"

    for i in range(data_1p.shape[0]):
        text += "0.0\t" + str(round(data_1p[i, 1], 8)) + "\t0.0\n"
    text = text[:-1]

    f = open(magnetic_field_file_name_one_pole, "w")
    f.write(text)
    f.close()

    print("file " + magnetic_field_file_name_one_pole + " created")
