import argparse
from utils import add_common_env_args, config2args

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate ETISS Perf build commands"
    )

    # Environment / execution mode
    add_common_env_args(parser)

    # Versions / naming
    parser.add_argument(
        "--ubuntu-versions",
        nargs="+",
        default=["20.04", "22.04", "24.04"],
        help="Ubuntu versions to build for"
    )

    parser.add_argument(
        "--etiss-ref",
        default="v0.11.2",
        help="ETISS git tag or ref"
    )
    parser.add_argument(
        "--etiss-perf-ref",
        # default="v0.10",
        default="main",
        help="ETISS Perf git tag or ref"
    )

    parser.add_argument(
        "--custom-name",
        default=None,
        help="Custom release name override"
    )

    return parser.parse_args()

args = parse_args()

GITHUB = args.GITHUB
CI = args.CI

UBUNTU_VERSIONS = args.ubuntu_versions
ETISS_REF = args.etiss_ref
ETISS_PERF_REF = args.etiss_perf_ref
CUSTOM_NAME = args.custom_name


SCRIPT = "./build-riscv-tools.sh"

JSON = CI and GITHUB

if GITHUB:
    if CI:
        OUT_DIR = "$GITHUB_WORKSPACE/upload"
    else:
        OUT_DIR = "/nas/lrz/home/ga87puy/RISCV-TC/github"
else:
    OUT_DIR = "/nas/lrz/home/ga87puy/RISCV-TC/syncandshare/ETISSPerf/default"


TOOLS = ["etiss_perf"]

DEFAULT_ARGS = ["--compress", "--force", "--setup", *TOOLS]
# TODO: auto cleanup?


DEFAULT_CONFIG = {}

DEFAULT_CONFIG["ETISS_REF"] = ETISS_REF
DEFAULT_CONFIG["ETISS_PERF_REF"] = ETISS_PERF_REF


VARIANTS = [
    ("default", {}),
]


cmds = []

extra = None
etiss_version = ETISS_REF
etiss_perf_version = ETISS_PERF_REF
if GITHUB:
    tag = f"etiss_perf_{CUSTOM_NAME or etiss_perf_version}"
    if etiss_version not in [None, "master"]:
        tag += f"_etiss_{etiss_version}"
    dest = f"{OUT_DIR}/{tag}/"
else:
    dest = f"{OUT_DIR}/{CUSTOM_NAME or etiss_perf_version}/Ubuntu"

if GITHUB:
    temp = ""
    if ETISS_REF:
        assert extra is None
        extra = f"ETISS {etiss_version}"
    if ETISS_PERF_REF:
        temp = etiss_perf_version
        if extra:
            temp = f" ({temp}, {extra})"
    if not JSON:
        print(f"mkdir -p {dest}")
    LABEL = f"ETISS Perf{temp}"
    tools_filtered = [tool.upper() for tool in TOOLS if tool != "etiss_perf"]
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
            name = f"etiss-perf-x86_64-linux-gnu-ubuntu-{ubuntu_version}"
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
            if tool == "etiss_perf":
                moves += [f"mv {dest__}/etiss_perf.tar.xz {dest__}.tar.xz"]
                src_dest = dest__.replace(f"x86_64-linux-gnu-ubuntu-{ubuntu_version}", "src")
                moves += [f"mv {dest__}/etiss_perf_src.tar.gz {src_dest}.tar.gz"]
            else:
                assert GITHUB
                assert triple is not None
                assert tool in ["pk", "htif"]
                tool_dest = dest__.replace(f"x86_64-linux-ubuntu-{ubuntu_version}", tool)
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
