file=$(readlink -f "${BASH_SOURCE:-$0}")
cfg_dir="$(dirname "$file")"

. $cfg_dir/riscv_gcc_default.sh
. $cfg_dir/htif_default.sh
. $cfg_dir/llvm_default.sh
. $cfg_dir/spike_default.sh
. $cfg_dir/etiss_default.sh
. $cfg_dir/etiss_perf_default.sh
