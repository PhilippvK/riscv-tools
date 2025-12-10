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
    OUT_DIR = "/nas/lrz/home/ga87puy/RISCV-TC/syncandshare/ETISS/default"


TOOLS = ["etiss"]

DEFAULT_ARGS = ["--compress", "--force", "--setup", *TOOLS]
# TODO: auto cleanup?


DEFAULT_CONFIG = {}

UBUNTU_VERSIONS = ["20.04", "22.04", "24.04"]
# UBUNTU_VERSIONS = ["20.04", "22.04"]
# UBUNTU_VERSIONS = ["22.04", "24.04"]
# UBUNTU_VERSIONS = ["20.04", "22.04"]
# UBUNTU_VERSIONS = ["20.04"]

ETISS_REF = "v0.11.2"

CUSTOM_NAME = None
# CUSTOM_NAME = "2024.09.03"


DEFAULT_CONFIG["ETISS_REF"] = ETISS_REF


VARIANTS = [
    ("default", {}),
]


cmds = []

extra = None
etiss_version = ETISS_REF
if GITHUB:
    tag = f"etiss_{CUSTOM_NAME or etiss_version}"
    dest = f"{OUT_DIR}/{tag}/"
else:
    dest = f"{OUT_DIR}/{CUSTOM_NAME or etiss_version}/Ubuntu"

if GITHUB:
    temp = ""
    if ETISS_REF:
        temp = etiss_version
        if extra:
            temp = f" ({temp}, {extra})"
    if not JSON:
        print(f"mkdir -p {dest}")
    LABEL = f"ETISS {temp}"
    tools_filtered = [tool.upper() for tool in TOOLS if tool != "etiss"]
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
            name = f"etiss-x86_64-linux-gnu-ubuntu-{ubuntu_version}"
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
            if tool == "etiss":
                moves += [f"mv {dest__}/etiss.tar.xz {dest__}.tar.xz"]
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
