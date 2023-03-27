import os
import platform

static_folder = os.path.join(os.path.dirname(__file__), "static")

architecure = platform.architecture()[0]

if architecure == "32bit":
    architecure = "386"
elif architecure == "64bit":
    architecure = "amd64"

operating_system = platform.system().lower()

executable = os.path.join(
    static_folder,
    "executables",
    operating_system,
    architecure,
    "selfbot.exe" if os.name == "nt" else "selfbot"
)

features_path = os.path.join(static_folder, "features.json")

if not os.path.exists(executable):
    print(f"Executable not found at path {executable}")
    exit(1)

if operating_system == "linux":
    os.system(f"chmod +x {executable}")

os.system(f"{executable} -featurelist > {features_path}")
