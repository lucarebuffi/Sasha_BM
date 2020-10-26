from time_domain.multi_energy_radiation_at_focus import run_script
import sys

if __name__ == "__main__":
    what = sys.argv[1]

    if what == "ME_F":
        run_script(sys.argv[2:])
