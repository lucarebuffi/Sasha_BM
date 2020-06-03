from frequency_domain.power_density_at_focus import run_script as run_PD
import sys

if __name__ == "__main__":
    what = sys.argv[1]

    if what == "PD":
        run_PD(sys.argv[2:])
