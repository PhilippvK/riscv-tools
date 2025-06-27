SCRIPT = "./build-riscv-tools.sh"

GITHUB = True

if GITHUB:
    OUT_DIR = "/nas/lrz/home/ga87puy/RISCV-TC/github"
else:
    OUT_DIR = "/nas/lrz/home/ga87puy/RISCV-TC/syncandshare/GCC/default"

DEFAULT_ARGS = ["--compress", "--force", "--setup", "gcc"]

# TODO: auto cleanup?


DEFAULT_CONFIG = {}

UBUNTU_VERSIONS = ["20.04", "22.04", "24.04"]
# UBUNTU_VERSIONS = ["22.04", "24.04"]
# UBUNTU_VERSIONS = ["20.04", "22.04"]
# UBUNTU_VERSIONS = ["20.04"]

# GNU_REF = "2024.09.03"  # random tag with gcc13
# GNU_REF = "2024.10.23"  # first tag with gcc14
GNU_REF = "2025.05.10"  # last tag with gcc14
# GNU_REF = "2025.05.22"  # first tag with gcc15
## GNU_REF = "2025.06.13"  # current latest tag

GCC_REF = None
# GCC_REF = "releases/gcc-13"

CUSTOM_NAME = None
# CUSTOM_NAME = "2024.09.03"


DEFAULT_CONFIG["GNU_REF"] = GNU_REF
if GCC_REF:
    DEFAULT_CONFIG["GCC_REF"] = GCC_REF

VARIANTS = [
    ("multilib_default", {"MULTILIB": True}),
    ("multilib_default_medany", {"MULTILIB": True, "CMODEL": "medany"}),
    ("multilib_default_linux_medany", {"MULTILIB": True, "LINUX": True, "CMODEL": "medany"}),
    ("multilib_large", {"MULTILIB": True, "MULTILIB_LARGE": True}),
    ("multilib_large_medany", {"MULTILIB": True, "MULTILIB_LARGE": True, "CMODEL": "medany"}),
    ("multilib_large_linux_medany", {"MULTILIB": True, "MULTILIB_LARGE": True, "LINUX": True, "CMODEL": "medany"}),
    ("rv32gc_ilp32d", {"ARCH": "rv32gc", "ABI": "ilp32d"}),
    ("rv32gcv_ilp32d", {"ARCH": "rv32gcv", "ABI": "ilp32d"}),
    ("rv32im_zicsr_zifencei_ilp32", {"ARCH": "rv32im_zicsr_zifencei", "ABI": "ilp32"}),
    ("rv32im_zicsr_zifencei_zve32x_ilp32", {"ARCH": "rv32im_zicsr_zifencei_zve32x", "ABI": "ilp32"}),
    ("rv64gc_lp64d", {"ARCH": "rv64gc", "ABI": "lp64d"}),
    ("rv64gcv_lp64d", {"ARCH": "rv64gcv", "ABI": "lp64d"}),
    ("rv64gc_lp64d_linux_medany", {"ARCH": "rv64gc", "ABI": "lp64d", "LINUX": True, "CMODEL": "medany"}),
    ("rv64gcv_lp64d_linux_medany", {"ARCH": "rv64gcv", "ABI": "lp64d", "LINUX": True, "CMODEL": "medany"}),
    ("rv64gc_lp64d_linux_musl_medany", {"ARCH": "rv64gc", "ABI": "lp64d", "LINUX": True, "CMODEL": "medany", "MUSL": True}),
    ("rv64gcv_lp64d_linux_musl_medany", {"ARCH": "rv64gcv", "ABI": "lp64d", "LINUX": True, "CMODEL": "medany", "MUSL": True}),
]


cmds = []

extra = None
if GITHUB:
    tag = f"gcc_{CUSTOM_NAME or GNU_REF}"
    if GCC_REF is not None and "releases/gcc-" in GCC_REF:
        gcc_ver = GCC_REF.split("-", 1)[-1]
        extra = f"GCC {gcc_ver}"
    dest = f"{OUT_DIR}/{tag}/"
else:
    dest = f"{OUT_DIR}/{CUSTOM_NAME or GNU_REF}/Ubuntu"

if GITHUB:
    temp = ""
    if GNU_REF:
        temp = GNU_REF
        if extra:
            temp = f" ({temp}, {extra})"
    print(f"mkdir -p {dest}")
    print(f"echo 'RISC-V GNU Tools {temp}' > {dest}/label.txt")

def config2args(cfg):
    def helper(val):
        if isinstance(val, bool):
            val = str(val).lower()
        return val

    assert isinstance(cfg, dict)
    return [f"{key}={helper(val)}" for key, val in cfg.items()]


for ubuntu_version in UBUNTU_VERSIONS:
    if GITHUB:
        dest_ = dest
    else:
        dest_ = f"{dest}/{ubuntu_version}"
    image = f"ubuntu:{ubuntu_version}"
    for variant, variant_config in VARIANTS:
        if GITHUB:
            arch = variant_config.get("ARCH", "rv64gc")
            abi = variant_config.get("ABI", "lp64d")
            xlen = int(arch[2:4])
            linux = variant_config.get("LINUX", False)
            tc = "linux" if linux else "elf"
            musl = variant_config.get("MUSL", False)
            libc = "" if not linux else ("musl" if musl else "glibc")
            if libc:
                tc = f"{tc}-{libc}"
            vendor = "unknown"
            triple = f"riscv{xlen}-{vendor}-{tc}"
            variant_ = variant
            if linux:
                variant_ = variant_.replace("_linux", "")
            if musl:
                variant_ = variant_.replace("_musl", "")
            name = f"{triple}-ubuntu-{ubuntu_version}-{variant}"
            dest__ = f"{dest_}/{name}"
        else:
            dest__ = f"{dest_}/{variant}"
        config = {
            **DEFAULT_CONFIG,
            **variant_config,
        }
        config_args = config2args(config)
        args = [SCRIPT, *DEFAULT_ARGS, "--docker", image, "--dest", dest__, *config_args]
        cmd = " ".join(args)
        cmd = f"mkdir -p {dest__} && {cmd} && mv {dest__}/gnu.tar.xz {dest__}.tar.xz"
        # TODO: rm dir (sudo?)
        cmds.append(cmd)

print("\n".join(cmds))
