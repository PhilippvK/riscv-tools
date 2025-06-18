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

### Building new toolchains (via Docker)

TODO

### Uploading new toolchains

TODO
