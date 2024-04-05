#
# LibreQuake Map Builder Python Script
# v0.0.3
# ---
# MissLavander-LQ & cypress/MotoLegacy & ZungryWare/ZungrySoft
#
import os
import subprocess
import sys
import shutil
from multiprocessing import Pool

# Map compiler paths
LQ_BSP_PATH = "qbsp"
LQ_VIS_PATH = "vis"
LQ_LIG_PATH = "light"

# Location of per-map compilation argument paths
LQ_MAP_CON_PATH = "./src/-buildconfigs-"

# Location of .map source files
LQ_MAP_SRC_PATH = "src"

# Default compilation flags
LQ_DEF_BSP_FLAGS = ""
LQ_DEF_VIS_FLAGS = ""
LQ_DEF_LIG_FLAGS = "-bounce -dirt"


# Check for compiler
def check_for_compiler():
    if not LQ_BSP_PATH:
        if not shutil.which('qbsp'):
            print("Couldn't find ericw-tools, required to build map content.")
            print("Please see https://github.com/ericwa/ericw-tools/ for info.")
            sys.exit()


# Setup compile arguments
def get_compile_args(path):
    LQ_BSP_FLAGS = LQ_DEF_BSP_FLAGS
    LQ_VIS_FLAGS = LQ_DEF_VIS_FLAGS
    LQ_LIG_FLAGS = LQ_DEF_LIG_FLAGS

    config_path = os.path.join(LQ_MAP_CON_PATH, f"{path[6:-4]}.conf")
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            for line in file:
                if line.startswith("LQ_BSP_FLAGS"):
                    LQ_BSP_FLAGS = line.split("\"")[1]
                if line.startswith("LQ_VIS_FLAGS"):
                    LQ_VIS_FLAGS = line.split("\"")[1]
                if line.startswith("LQ_LIG_FLAGS"):
                    LQ_LIG_FLAGS = line.split("\"")[1]
    return LQ_BSP_FLAGS, LQ_VIS_FLAGS, LQ_LIG_FLAGS


# Execute command
def execute_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in process.stdout:
        line = line.decode().strip()
        if "WARNING" in line or "Leak" in line:
            print(line)


# Find all files in directory with this extension
def find(directory, ext):
    result_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(ext):
                result_list.append(os.path.join(root, file))
    return result_list


def move_file(src, dest_dir):
    # Get the base filename
    filename = os.path.basename(src)

    # Construct the full path for the destination file
    dest_file = os.path.join(dest_dir, filename)

    # Check if the destination file exists and remove it if it does
    if os.path.isfile(dest_file):
        os.remove(dest_file)

    # Move the source file to the destination directory
    shutil.move(src, dest_file)


def process_map(map_path):
    map_name = os.path.splitext(os.path.basename(map_path))[0]
    print(f"Compiling f{map_name}")
    LQ_BSP_FLAGS, LQ_VIS_FLAGS, LQ_LIG_FLAGS = get_compile_args(map_name)
    workdir = os.path.dirname(map_path)
    print(f"- Bsp {map_name}")
    subprocess.call([LQ_BSP_PATH] + LQ_BSP_FLAGS.split() + [f"{map_name}.map"], stdout=subprocess.DEVNULL, cwd=workdir)
    print(f"- Vis {map_name}")
    subprocess.call([LQ_VIS_PATH] + LQ_VIS_FLAGS.split() + [f"{map_name}.bsp"], stdout=subprocess.DEVNULL, cwd=workdir)
    print(f"- Light {map_name}")
    subprocess.call([LQ_LIG_PATH] + LQ_LIG_FLAGS.split() + [f"{map_name}.bsp"], stdout=subprocess.DEVNULL, cwd=workdir)
    print(f"Finished compiling {map_name}")


# Command make
def command_make(specific_map=None, max_workers=4):
    check_for_compiler()

    maps = [f for f in find(os.getcwd(), ".map") if "skip" not in f and "archive" not in f and "autosave" not in f]

    if specific_map:
        maps = [f for f in maps if specific_map in f]

    with Pool(processes=max_workers) as pool:
        pool.map(process_map, maps)

    # Move bsp and lit files into the /lq1/maps directory
    print("Moving files...")
    for ext in [".bsp", ".lit"]:
        for file in find("./src", ext):
            move_file(file, "./")

    print("* Build DONE")


# Command single
def command_single(map_name):
    if not map_name:
        print("Map name needed, e.g. 'e1m1'")
        return
    command_make(map_name)


# Command clean
def command_clean():
    for ext in [".bsp", ".lit", ".prt", ".texinfo", ".texinfo.json", ".pts", ".log"]:
        for file in find('./', ext):
            os.remove(file)
    print("* Clean DONE")


# Command help
def command_help():
    help_text = """
                 LibreQuake make.py Map Builder Script /// v0.0.3
    ==========================================================================
    This script requires ericw-tools (https://github.com/ericwa/ericw-tools/).
    --------------------------------------------------------------------------
    Usage: make.py [OPERATION] [FLAGS]

    OPERATIONS:
    -h, help           read this msg :3
    -c, clean          remove extra files that are left after build
    -m, make           compile all available map OR
    -s, single <MAP>   compile a specified single map

    FLAGS:
    QBSP_FLAGS    override map-specific qbsp flags with a global setting
    QBSP_PATH     use a local path for qbsp instead of checking $PATH
    VIS_FLAGS     override map-specific vis flags with a global setting
    VIS_PATH     use a local path for qbsp instead of checking $PATH
    LIGHT_FLAGS   override map-specific light flags with a global setting
    LIGHT_PATH     use a local path for qbsp instead of checking $PATH

    Example: make.py -m LIGHT_FLAGS=\"-extra4 -bounce\" QBSP_PATH=\"~/qbsp\"
    Example: make.py -s e1/e1m1
    ==========================================================================
    """
    print(help_text)


# Argument parsing
def parse_args(args):
    operations = {
        '-m': command_make,
        '-s': lambda: command_single(args[1] if len(args) > 1 else None),
        '-c': command_clean,
        '-h': command_help,
    }

    operation = operations.get(args[0], command_help)
    operation()


# If being run from the command line
if __name__ == "__main__":
    if (len(sys.argv) > 1):
        parse_args(sys.argv[1:])
    else:
        command_help()

# If being run from build.py
if __name__ == "__build__":
    command_make()
