# riscv-tools
Binary distributions for RISC-V development tools (GNU/GCC Toolchain, LLVM, Simulators,...)

See [Releases](https://github.com/PhilippvK/riscv-tools/releases) or [Tags](https://github.com/PhilippvK/riscv-tools/tags)!

Download links without redirecting (for WGET/CURL) follow this pattern:

```
https://github.com/PhilippvK/riscv-tools/releases/download/gnu_2025.06.13/riscv64-unknown-linux-glibc-ubuntu-20.04-rv64gc_lp64d_linux_medany.tar.xz
...
```

## Supported OSes

Images for the following OSes are provided:

- Ubuntu 20.04
- Ubuntu 22.04
- Ubuntu 24.04

## Supported Tools

### LLVM/Clang

#### Flags

The following flags are used for building LLVM/Clang:

```sh
TODO
```

#### Versions

We aim to provide at least one build per major release (i.e. `llvm_19.1.1`, `llvm_20.1.7`).

### RISC-V GNU Toolchain

#### Variants

We are building several multilib and non-multilib versions:

- `multilib_default`
- `multilib_large`
- ...

**Why do we need non-multilib builds at all?:** Clang's multilib-support for baremetal RISC-V is either broken or basically non-existent. Hence, multilib GNU toolchains can not be used with LLVM.

#### Versions

We aim to provide at least one set of builds per major GCC release (i.e. 13, 14, 15). Since there is no verioning in [`riscv-gnu-toolchain`](https://github.com/riscv-collab/riscv-gnu-toolchain), nightly builds (i.e. `gnu_2025.06.13`) are used as tags.

## Contributions

### Issue Tracking

If a specific version (i.e. LLVM 21) or configuration (i.e. `rv32imaf_ilp32f`) of a tool is missing please open up new issue!

## Usage

### Configuration variables

the following variables can be overriden by passing i.e. `LINUX=true` as argument to the `build-riscv-tools.sh` script.

```sh
HOST= # Can be used to run the script on another hist via SSH
DEST= # Destination directory for final artifacts
IMAGE= # Docker image to be used (i.e. ubuntu:22.04)
VERBOSE=false # Enable verbose logging
SETUP=false # Enable automatic installtions of OS packages via APT (recommended for docker mode)
LOGDIR= # Custom loging dir
COMPRESS=false # Compress output files
COMPRESS_EXT=tar.xz # Used compression format
COMPRESS_LEVEL=7 # Used compression level
COMPRESS_KEEP=false # Keep uncompressed files, too
FORCE=false # Override existing files
CLEANUP=false # Remove temporary files
CFG=default
USER_CFG=
WORKDIR=
RISCV_HOST=auto
# RISCV_HOST=
VENDOR=unknown
ARCH=
ABI=
CMODEL=
LINUX=false
MUSL=false
MULTILIB=false
MULTILIB_LARGE=false
MULTILIB_DEFAULT_GENERATOR=""
MULTILIB_LARGE_GENERATOR="rv32e-ilp32e--zicsr*zifencei rv32ea-ilp32e--zicsr*zifencei rv32eac-ilp32e--zicsr*zifencei rv32ec-ilp32e--zicsr*zifencei rv32em-ilp32e--zicsr*zifencei rv32ema-ilp32e--zicsr*zifencei rv32emac-ilp32e--zicsr*zifencei rv32emc-ilp32e--zicsr*zifencei rv32i-ilp32--zicsr*zifencei rv32ia-ilp32--zicsr*zifencei rv32iac-ilp32--zicsr*zifencei rv32iaf-ilp32f--zicsr*zifencei rv32iafc-ilp32f--zicsr*zifencei rv32iafd-ilp32d--zicsr*zifencei rv32iafdc-ilp32d--zicsr*zifencei rv32ic-ilp32--zicsr*zifencei rv32if-ilp32f--zicsr*zifencei rv32ifc-ilp32f--zicsr*zifencei rv32ifd-ilp32d--zicsr*zifencei rv32ifdc-ilp32d--zicsr*zifencei rv32im-ilp32--zicsr*zifencei rv32ima-ilp32--zicsr*zifencei rv32imaf-ilp32f--zicsr*zifencei rv32imafc-ilp32f--zicsr*zifencei rv32imafd-ilp32d--zicsr*zifencei rv32imafdc-ilp32d--zicsr*zifencei rv32imc-ilp32--zicsr*zifencei rv32imf-ilp32f--zicsr*zifencei rv32imfc-ilp32f--zicsr*zifencei rv32imfd-ilp32d--zicsr*zifencei rv32imfdc-ilp32d--zicsr*zifencei rv64i-lp64--zicsr*zifencei rv64ia-lp64--zicsr*zifencei rv64iac-lp64--zicsr*zifencei rv64iaf-lp64f--zicsr*zifencei rv64iafc-lp64f--zicsr*zifencei rv64iafd-lp64d--zicsr*zifencei rv64iafdc-lp64d--zicsr*zifencei rv64ic-lp64--zicsr*zifencei rv64if-lp64f--zicsr*zifencei rv64ifc-lp64f--zicsr*zifencei rv64ifd-lp64d--zicsr*zifencei rv64ifdc-lp64d--zicsr*zifencei rv64im-lp64--zicsr*zifencei rv64ima-lp64--zicsr*zifencei rv64imac-lp64--zicsr*zifencei rv64imaf-lp64f--zicsr*zifencei rv64imafc-lp64f--zicsr*zifencei rv64imafd-lp64d--zicsr*zifencei rv64imafdc-lp64d--zicsr*zifencei rv64imc-lp64--zicsr*zifencei rv64imf-lp64f--zicsr*zifencei rv64imfc-lp64f--zicsr*zifencei rv64imfd-lp64d--zicsr*zifencei rv64imfdc-lp64d--zicsr*zifencei"
ENABLE_GCC=false
ENABLE_SPIKE=false
ENABLE_SPIKE_MIN=false
ENABLE_PK=false
ENABLE_ETISS=false
ENABLE_LLVM=false
ENABLE_HTIF=false
ENABLE_CCACHE=true
ENABLE_MGCLIENT=false
ENABLE_CDFG_PASS=false
SHARED_CCACHE_DIR=
LLVM_DEPTH=
CMAKE_GENERATOR=Ninja
CMAKE_BUILD_TYPE=Release
GIT_FILTER=true  # TODO
```

### Building new toolchains/tools (via Docker)

#### GCC/GCU

Single build (non-multilib):

```sh
./build-riscv-tools.sh --compress --force --setup gcc --docker ubuntu:24.04 --dest /path/to/output/gcc_2025.06.13/riscv64-unknown-linux-musl-ubuntu-24.04-rv64gcv_lp64d_linux_musl_medany GNU_REF=2025.06.13 ARCH=rv64gcv ABI=lp64d LINUX=true CMODEL=medany MUSL=true
```

Single build (multilib):

```sh
./build-riscv-tools.sh --compress --force --setup gcc --docker ubuntu:22.04 --dest /path/to/output/gcc_2025.06.13/riscv64-unknown-elf-ubuntu-22.04-multilib_large GNU_REF=2025.06.13 MULTILIB=true MULTILIB_LARGE=true
```

Generate commands automatically:

```sh
# Edit before to change matrix
python3 gen_gcc_cmds.py
```

#### LLVM

```sh
./build-riscv-tools.sh --docker ubuntu:20.04 --dest /path/to/output/llvm_20.1.7/clang+llvm-20.1.7-x86_64-linux-gnu-ubuntu-20.04/ --compress --setup llvm LLVM_REF=llvmorg-20.1.7
```
TODO

### Uploading new toolchains

TODO
