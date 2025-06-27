
export LLVM_URL=https://github.com/llvm/llvm-project.git
export LLVM_REF=main

export LLVM_ENABLE_PROJECTS="clang;lld"
export LLVM_TARGETS_TO_BUILD="X86;RISCV"
export LLVM_OPTIMIZED_TABLEGEN=ON
export LLVM_ENABLE_ASSERTIONS=OFF
export LLVM_CCACHE_BUILD=OFF
export LLVM_PARALLEL_LINK_JOBS=8  # TODO: auto
export LLVM_BUILD_TOOLS=ON
# export LLVM_USE_LINKER=gold
# export LLVM_DEFAULT_TARGET_TRIPLE=riscv32-unknown-elf-
# export LLVM_ENABLE_RUNTIMES="compiler-rt;libcxx;libcxxabi;libunwind"
# export DEFAULT_SYSROOT="../sysroot"
# export LLVM_RUNTIME_TARGETS=?
# export LLVM_INSTALL_TOOLCHAIN_ONLY=ON
