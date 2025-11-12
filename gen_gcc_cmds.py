SCRIPT = "./build-riscv-tools.sh"

GITHUB = True
CI = True

JSON = CI and GITHUB

if GITHUB:
    if CI:
        OUT_DIR = "$GITHUB_WORKSPACE/upload"
    else:
        OUT_DIR = "/nas/lrz/home/ga87puy/RISCV-TC/github"
else:
    OUT_DIR = "/nas/lrz/home/ga87puy/RISCV-TC/syncandshare/GCC/default"


TOOLS = ["gcc"]

HTIF = True  # Warning: not compatible with Linux toolchain!
PK = True

if HTIF:
    TOOLS += ["htif"]
if PK:
    TOOLS += ["pk"]

DEFAULT_ARGS = ["--compress", "--force", "--setup", *TOOLS]



# TODO: auto cleanup?


DEFAULT_CONFIG = {}

UBUNTU_VERSIONS = ["20.04", "22.04", "24.04"]
# UBUNTU_VERSIONS = ["20.04", "22.04"]
# UBUNTU_VERSIONS = ["22.04", "24.04"]
# UBUNTU_VERSIONS = ["20.04", "22.04"]
# UBUNTU_VERSIONS = ["20.04"]

# GNU_REF = "2024.09.03"  # random tag with gcc13
# GNU_REF = "2024.10.23"  # first tag with gcc14
# GNU_REF = "2025.05.10"  # last tag with gcc14
# GNU_REF = "2025.05.22"  # first tag with gcc15
## GNU_REF = "2025.06.13"  # current latest tag
GNU_REF = "2025.08.08"

GCC_REF = None
# GCC_REF = "releases/gcc-13"

CUSTOM_NAME = None
# CUSTOM_NAME = "2024.09.03"


DEFAULT_CONFIG["SHARED_CCACHE_DIR"] = "$(pwd)/.ccache"
DEFAULT_CONFIG["GNU_REF"] = GNU_REF
if GCC_REF:
    DEFAULT_CONFIG["GCC_REF"] = GCC_REF


RV32 = True
RV64 = True
MULTILIB_DEFAULT = True
MULTILIB_LARGE = True
NON_MULTILIB = True
RVV = True
LINUX = True
MUSL = True
GLIBC = True

VARIANTS = [
    *([("multilib_default", {"MULTILIB": True})] if MULTILIB_DEFAULT else []),
    *([("multilib_default_medany", {"MULTILIB": True, "CMODEL": "medany"})] if MULTILIB_DEFAULT else []),
    *([("multilib_default_linux_medany", {"MULTILIB": True, "LINUX": True, "CMODEL": "medany"})] if MULTILIB_DEFAULT and LINUX and GLIBC else []),
    *([("multilib_default_linux_musl_medany", {"MULTILIB": True, "LINUX": True, "CMODEL": "medany", "MUSL": True})] if MULTILIB_DEFAULT and LINUX and MUSL else []),
    *([("multilib_large", {"MULTILIB": True, "MULTILIB_LARGE": True})] if MULTILIB_LARGE else []),
    *([("multilib_large_medany", {"MULTILIB": True, "MULTILIB_LARGE": True, "CMODEL": "medany"})] if MULTILIB_LARGE else []),
    *([("multilib_large_linux_medany", {"MULTILIB": True, "MULTILIB_LARGE": True, "LINUX": True, "CMODEL": "medany"})] if MULTILIB_LARGE and LINUX and GLIBC else []),
    *([("multilib_large_linux_musl_medany", {"MULTILIB": True, "MULTILIB_LARGE": True, "LINUX": True, "CMODEL": "medany", "MUSL": True})] if MULTILIB_LARGE and LINUX and MUSL else []),
    *([("rv32gc_ilp32d", {"ARCH": "rv32gc", "ABI": "ilp32d"})] if NON_MULTILIB and RV32 else []),
    *([("rv32gcv_ilp32d", {"ARCH": "rv32gcv", "ABI": "ilp32d"})] if NON_MULTILIB and RV32 and RVV else []),
    *([("rv32im_zicsr_zifencei_ilp32", {"ARCH": "rv32im_zicsr_zifencei", "ABI": "ilp32"})] if NON_MULTILIB and RV32 else []),
    *([("rv32im_zicsr_zifencei_zve32x_ilp32", {"ARCH": "rv32im_zicsr_zifencei_zve32x", "ABI": "ilp32"})] if NON_MULTILIB and RV32 and RVV else []),
    *([("rv64gc_lp64d", {"ARCH": "rv64gc", "ABI": "lp64d"})] if NON_MULTILIB and RV64 else []),
    *([("rv64gcv_lp64d", {"ARCH": "rv64gcv", "ABI": "lp64d"})] if NON_MULTILIB and RV64 and RVV else []),
    *([("rv64gc_lp64d_linux_medany", {"ARCH": "rv64gc", "ABI": "lp64d", "LINUX": True, "CMODEL": "medany"})] if NON_MULTILIB and RV64 and LINUX and GLIBC else []),
    *([("rv64gcv_lp64d_linux_medany", {"ARCH": "rv64gcv", "ABI": "lp64d", "LINUX": True, "CMODEL": "medany"})] if NON_MULTILIB and RV64 and RVV and LINUX and GLIBC else []),
    *([("rv64gc_lp64d_linux_musl_medany", {"ARCH": "rv64gc", "ABI": "lp64d", "LINUX": True, "CMODEL": "medany", "MUSL": True})] if NON_MULTILIB and RV64 and LINUX and MUSL else []),
    *([("rv64gcv_lp64d_linux_musl_medany", {"ARCH": "rv64gcv", "ABI": "lp64d", "LINUX": True, "CMODEL": "medany", "MUSL": True})] if NON_MULTILIB and RV64 and RVV and LINUX and MUSL else []),
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
    if not JSON:
        print(f"mkdir -p {dest}")
    LABEL = f"RISC-V GNU Tools {temp}"
    tools_filtered = [tool.upper() for tool in TOOLS if tool not in ["gcc", "gnu"]]
    if len(tools_filtered) > 0:
        tools_str = " + ".join(tools_filtered)
        LABEL = f"{LABEL} + {tools_str}"
    if not JSON:
        print(f"echo '{LABEL}' > {dest}/label.txt")

def config2args(cfg):
    def helper(val):
        if isinstance(val, bool):
            val = str(val).lower()
        return val

    assert isinstance(cfg, dict)
    return [f"{key}={helper(val)}" for key, val in cfg.items()]


# from collections import defaultdict
# release2commands = defaultdict(list)
json_data = {
    "releases": [
        {
            "tag": tag,
            "title": LABEL,
            "dest": f"{OUT_DIR}/{tag}",
            "commands": [],
        }
    ]
}

for ubuntu_version in UBUNTU_VERSIONS:
    if GITHUB:
        dest_ = dest
    else:
        dest_ = f"{dest}/{ubuntu_version}"
    image = f"ubuntu:{ubuntu_version}"
    for variant, variant_config in VARIANTS:
        triple = None
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
            vendor = "unknown"  # TODO: get from config
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
        moves = []
        for tool in TOOLS:
            if tool in ["gcc", "gnu"]:
                moves += [f"mv {dest__}/gnu.tar.xz {dest__}.tar.xz"]
            else:
                assert GITHUB
                assert triple is not None
                assert tool in ["pk", "htif"]
                tool_dest = dest__.replace(f"{triple}-ubuntu-{ubuntu_version}", tool)
                moves += [f"mv {dest__}/{tool}.tar.xz {tool_dest}.tar.xz"]
        move_cmds = " && ".join(moves)
        cmd = f"mkdir -p {dest__} && {cmd} && {move_cmds}"
        # TODO: rm dir (sudo?)
        cmds.append(cmd)
        json_data["releases"][0]["commands"].append(cmd)



if JSON:
    import json
    print(json.dumps(json_data, indent=2))
else:
    print("\n".join(cmds))
