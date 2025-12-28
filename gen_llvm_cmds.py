import argparse
from utils import add_common_env_args, config2args

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate LLVM build commands"
    )

    # Environment / execution mode
    add_common_env_args(parser)

    # Platform selection
    parser.add_argument(
        "--ubuntu-versions",
        nargs="+",
        default=["20.04", "22.04", "24.04"],
        help="Ubuntu versions to build for"
    )

    # Versioning
    parser.add_argument(
        "--llvm-ref",
        default="llvmorg-21.1.7",
        help="LLVM git tag or ref (e.g. llvmorg-21.1.7)"
    )

    parser.add_argument(
        "--custom-name",
        default=None,
        help="Override release name"
    )

    return parser.parse_args()

args = parse_args()

GITHUB = args.GITHUB
CI = args.CI

UBUNTU_VERSIONS = args.ubuntu_versions
LLVM_REF = args.llvm_ref
CUSTOM_NAME = args.custom_name

SCRIPT = "./build-riscv-tools.sh"

JSON = CI and GITHUB

if GITHUB:
    if CI:
        OUT_DIR = "$GITHUB_WORKSPACE/upload"
    else:
        OUT_DIR = "/nas/lrz/home/ga87puy/RISCV-TC/github"
else:
    OUT_DIR = "/nas/lrz/home/ga87puy/RISCV-TC/syncandshare/LLVM/default"


TOOLS = ["llvm"]

DEFAULT_ARGS = ["--compress", "--force", "--setup", *TOOLS]
# TODO: auto cleanup?

DEFAULT_CONFIG = {}

DEFAULT_CONFIG["SHARED_CCACHE_DIR"] = "$(pwd)/.ccache"
DEFAULT_CONFIG["LLVM_REF"] = LLVM_REF


VARIANTS = [
    ("default", {}),
]


cmds = []

extra = None
llvm_version = LLVM_REF.replace("llvmorg-", "")
if GITHUB:
    tag = f"llvm_{CUSTOM_NAME or llvm_version}"
    dest = f"{OUT_DIR}/{tag}/"
else:
    dest = f"{OUT_DIR}/{CUSTOM_NAME or llvm_version}/Ubuntu"

if GITHUB:
    temp = ""
    if LLVM_REF:
        temp = llvm_version
        if extra:
            temp = f" ({temp}, {extra})"
    if not JSON:
        print(f"mkdir -p {dest}")
    LABEL = f"LLVM {temp}"
    tools_filtered = [tool.upper() for tool in TOOLS if tool != "llvm"]
    if len(tools_filtered) > 0:
        tools_str = " + ".join(tools_filtered)
        LABEL = f"{LABEL} + {tools_str}"
    if not JSON:
        print(f"echo '{LABEL}' > {dest}/label.txt")


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
            name = f"clang+llvm-{llvm_version}-x86_64-linux-gnu-ubuntu-{ubuntu_version}"
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
            if tool == "llvm":
                moves += [f"mv {dest__}/llvm.tar.xz {dest__}.tar.xz"]
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
