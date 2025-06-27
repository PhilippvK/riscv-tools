#!/bin/bash

# TODO: make logging easier by using funcs
# TODO: docker image support

set -e
set -o pipefail

script=$(readlink -f "${BASH_SOURCE:-$0}")
dir="$(dirname "$script")"

export PATH=/usr/local/research/projects/SystemDesign/tools/cmake/3.22.2/bin:$PATH


HOST=
DEST=
IMAGE=
VERBOSE=false
SETUP=false
LOGDIR=
COMPRESS=false
COMPRESS_EXT=tar.xz
COMPRESS_LEVEL=7
COMPRESS_KEEP=false
FORCE=false
CLEANUP=false
CFG=default
USER_CFG=
WORKDIR=
RISCV_HOST=riscv32-unknown-elf
# RISCV_HOST=
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
ENABLE_PK=false
ENABLE_LLVM=false

CMAKE_GENERATOR=Ninja
CMAKE_BUILD_TYPE=Release



SSH_ARGS=
DOCKER_ARGS=

echo "> $0 $@"

print_help() {
   # Display Help
   echo "Add description of the script functions here."
   echo
   echo "Syntax: $0 [--host HOST] [--dest DEST] [--cfg CFG] [--workdir WORKDIR] [--docker IMAGE] [--verbose] [--setup] [--cleanup] [--force] [--compress] [--help] {gcc|llvm|spike|pk}"
   echo "options:"
   echo "--help     Print this Help."
   echo "TODO"
   echo
}

do_compress() {
    TO_COMPRESS=$1
    COMPRESS_EXT=$2
    COMPRESS_LEVEL=$3
    COMPRESS_KEEP=$4
    echo "Compressing $TO_COMPRESS ->  $TO_COMPRESS.$COMPRESS_EXT"
    if [[ "$COMPRESS_EXT" == "tar.xz" ]]
    then
        cd $TO_COMPRESS
        tar cf - * | xz -$COMPRESS_LEVEL --threads=`nproc` -c - > $TO_COMPRESS.$COMPRESS_EXT
        cd -
    # elif [[ "$COMPRESS_EXT" == "tar.gz" ]]
    # then

    # elif [[ "$COMPRESS_EXT" == "zip" ]]
    # then
    else
      echo "Unsupported ext: $COMPRESS_EXT"
      exit 1
    fi
    if [[ "$COMPRESS_KEEP" == "false" ]]
    then
        rm -r $TO_COMPRESS
    fi
}
export -f do_compress


POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --host)
      HOST="$2"
      shift # past argument
      shift # past value
      ;;
    -d|--dest)
      SSH_ARGS="${SSH_ARGS} ${1} ${2}"
      DEST="$2"
      shift # past argument
      shift # past value
      ;;
    --cfg)
      SSH_ARGS="${SSH_ARGS} ${1} ${2}"
      DOCKER_ARGS="${SSH_ARGS} ${1} ${2}"
      CFG="$2"
      shift # past argument
      shift # past value
      ;;
    --workdir)
      SSH_ARGS="${SSH_ARGS} ${1} ${2}"
      WORKDIR="$2"
      shift # past argument
      shift # past value
      ;;
    --docker)
      SSH_ARGS="${SSH_ARGS} ${1} ${2}"
      IMAGE="$2"
      shift # past argument
      shift # past value
      ;;
    --verbose)
      SSH_ARGS="${SSH_ARGS} ${1}"
      DOCKER_ARGS="${DOCKER_ARGS} ${1}"
      VERBOSE=true
      shift # past argument
      ;;
    --setup)
      SSH_ARGS="${SSH_ARGS} ${1}"
      DOCKER_ARGS="${DOCKER_ARGS} ${1}"
      SETUP=true
      shift # past argument
      ;;
    --cleanup)
      SSH_ARGS="${SSH_ARGS} ${1}"
      CLEANUP=true
      shift # past argument
      ;;
    -f|--force)
      SSH_ARGS="${SSH_ARGS} ${1}"
      DOCKER_ARGS="${DOCKER_ARGS} ${1}"
      FORCE=true
      shift # past argument
      ;;
    --compress)
      SSH_ARGS="${SSH_ARGS} ${1}"
      DOCKER_ARGS="${DOCKER_ARGS} ${1}"
      COMPRESS=true
      shift # past argument
      ;;
    -h|--help)
      print_help
      exit 0
      shift # past argument
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      SSH_ARGS="${SSH_ARGS} ${1}"
      DOCKER_ARGS="${DOCKER_ARGS} ${1}"
      if [[ "$1" == *"="* ]]
      then
          key=$(echo $1 | cut -d= -f1)
          value=$(echo $1 | cut -d= -f2)
          USER_CFG="$USER_CFG $key=$value"
          echo "$key=$value"
      elif [[ "$1" == "gcc" ]]
      then
          ENABLE_GCC=true
      elif [[ "$1" == "llvm" ]]
      then
          ENABLE_LLVM=true
      elif [[ "$1" == "spike" ]]
      then
          ENABLE_SPIKE=true
      elif [[ "$1" == "pk" ]]
      then
          ENABLE_PK=true
      else
          echo "Invalid positional argument: $1"
          exit 1
      fi
      shift # past argument
      ;;
  esac
done


# echo "SSH_ARGS $SSH_ARGS"

if [[ "$CFG" == "default" ]]
then
  . $dir/cfg/default.sh
else
  if [[ -f "$CFG" ]]
  then
    . $CFG
  else
    . $dir/cfg/$CFG.sh
  fi
fi
if [[ ! -z "$USER_CFG" ]]
then
  export $USER_CFG
fi

echo "HOST            = ${HOST}"
echo "DEST            = ${DEST}"
echo "VERBOSE         = ${VERBOSE}"
echo "SETUP           = ${SETUP}"
echo "LOGDIR          = ${LOGDIR}"
echo "WORKDIR         = ${WORKDIR}"
echo "COMPRESS        = ${COMPRESS}"
echo "COMPRESS_EXT    = ${COMPRESS_EXT}"
echo "COMPRESS_LEVEL  = ${COMPRESS_LEVEL}"
echo "COMPRESS_KEEP   = ${COMPRESS_KEEP}"
echo "FORCE           = ${FORCE}"
echo "CLEANUP         = ${CLEANUP}"
echo "ARCH            = ${ARCH}"
echo "ABI             = ${ABI}"
echo "CMODEL          = ${CMODEL}"
echo "LINUX           = ${LINUX}"
echo "MUSL            = ${MUSL}"
echo "MULTILIB        = ${MULTILIB}"
echo "MULTILIB_LARGE        = ${MULTILIB_LARGE}"
echo "MULTILIB_DEFAULT_GENERATOR        = ${MULTILIB_DEFAULT_GENERATOR}"
echo "MULTILIB_LARGE_GENERATOR        = ${MULTILIB_LARGE_GENERATOR}"
echo "ENABLE_GCC      = ${ENABLE_GCC}"
echo "ENABLE_SPIKE    = ${ENABLE_SPIKE}"
echo "ENABLE_PK       = ${ENABLE_PK}"
echo "ENABLE_LLVM     = ${ENABLE_LLVM}"
echo "CMAKE_GENERATOR = ${CMAKE_GENERATOR}"
echo "GNU_URL         = ${GNU_URL}"
echo "GNU_REF         = ${GNU_REF}"
echo "GCC_URL         = ${GCC_URL}"
echo "GCC_REF         = ${GCC_REF}"
echo "BINUTILS_URL    = ${BINUTILS_URL}"
echo "BINUTILS_REF    = ${BINUTILS_REF}"
echo "LLVM_URL        = ${LLVM_URL}"
echo "LLVM_REF        = ${LLVM_REF}"
echo "SPIKE_URL       = ${SPIKE_URL}"
echo "SPIKE_REF       = ${SPIKE_REF}"
echo "PK_URL          = ${PK_URL}"
echo "PK_REF          = ${PK_REF}"

if [[ ! -z "$HOST" ]]
then
    echo "Running on host: $HOST"
    echo ssh $HOST -C $script $SSH_ARGS
    ssh $HOST -C $script $SSH_ARGS
    exit $!
fi


if [[ -z "$DEST" ]]
then
    echo "Missing destination!"
    exit 1
fi

if [[ "$WORKDIR" == "" ]]
then
  WORKDIR=`mktemp -d`
  echo "WORKDIR=$WORKDIR"
fi

if [[ ! -z "$IMAGE" ]]
then
  echo "Running in docker image: $IMAGE"
  DOCKER_ARGS="$DOCKER_ARGS --dest /temp/install --force --setup"
  cp $script $WORKDIR
  cp -r $dir/cfg $WORKDIR/cfg
  # TODO: make rm optional
  docker run -it --rm -v $WORKDIR:/temp  $IMAGE /bin/bash -c "cd /temp && ./build-riscv-tools.sh $DOCKER_ARGS"
else
  # install git if not available (in docker)
  if [[ "$SETUP" == "true" ]]
  then
      export DEBIAN_FRONTEND=noninteractive
      apt update
      apt install -y git autoconf automake autotools-dev curl python3 python3-pip libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev ninja-build cmake libglib2.0-dev wget libzstd-dev python-is-python3
      version=3.27
      build=7
      ## don't modify from here
      limit=3.20
      result=$(echo "$version >= $limit" | bc -l)
      os=$([ "$result" == 1 ] && echo "linux" || echo "Linux")
      wget https://cmake.org/files/v$version/cmake-$version.$build-$os-x86_64.sh
      mkdir /opt/cmake
      sh cmake-$version.$build-$os-x86_64.sh --prefix=/opt/cmake --skip-license
      rm cmake-$version.$build-$os-x86_64.sh
      ls /opt/cmake
      export PATH=/opt/cmake/bin:$PATH
  fi
  cd $WORKDIR

  if [[ "$LOGDIR" == "" ]]
  then
    LOGDIR=$WORKDIR/logs
  fi
  mkdir -p $LOGDIR

  INSTALLDIR=$WORKDIR/install

  mkdir -p $INSTALLDIR

  if [[ "$ENABLE_GCC" == "true" ]]
  then
    echo "Installing riscv-gnu-tools ..."
    if [[ -d gnu ]]
    then
      echo "Skipping clone (already exists)"
    else
      git clone $GNU_URL gnu 2>&1 | tee -a $LOGDIR/gcc.log
    fi
    cd gnu
    if [[ "$GNU_REF" != "" ]]
    then
      git checkout $GNU_REF 2>&1 | tee -a $LOGDIR/gcc.log
    fi
    # git submodule update --init --recursive
    git submodule update --init --recursive -- binutils gcc glibc dejagnu gdb 2>&1 | tee -a $LOGDIR/gcc.log
    if [[ "$GCC_URL" != "" ]]
    then
      echo "SKIP"
    fi
    if [[ "$BINUTILS_URL" != "" ]]
    then
      echo "SKIP"
    fi
    if [[ "$GCC_REF" != "" ]]
    then
      git -C gcc checkout $GCC_REF 2>&1 | tee -a $LOGDIR/gcc.log
    fi
    if [[ "$BINUTILS_REF" != "" ]]
    then
      echo "SKIP"
    fi
    # git submodule update --init --recursive --depth 1 riscv-binutils riscv-gcc riscv-glibc riscv-dejagnu riscv-newlib riscv-gdb
    mkdir -p build
    cd build
    ARCH_ABI_ARGS=
    if [[ "$ARCH" != "" ]]
    then
      ARCH_ABI_ARGS="$ARCH_ABI_ARGS --with-arch=$ARCH"
    fi
    if [[ "$ABI" != "" ]]
    then
      ARCH_ABI_ARGS="$ARCH_ABI_ARGS --with-abi=$ABI"
    fi
    if [[ "$CMODEL" != "" ]]
    then
      ARCH_ABI_ARGS="$ARCH_ABI_ARGS --with-cmodel=$CMODEL"
    fi
    MULTILIB_ARGS=
    MULTILIB_GEN_ARGS=
    if [[ "$MULTILIB" == "true" ]]
    then
      MULTILIB_ARGS="$MUKTILIB_ARGS --enable-multilib"
      if [[ "$MULTILIB_LARGE" == "true" ]]
      then
        MULTILIB_GEN_ARGS="--with-multilib-generator=${MULTILIB_LARGE_GENERATOR}"
      else
        if [[ "$MULTILIB_DEFAULT_GENERATOR" != "" ]]
        then
          MULTILIB_GEN_ARGS="--with-multilib-generator=${MULTILIB_DEFAULT_GENERATOR}"
        fi
      fi
    fi
    TARGET_ARG=
    if [[ "$LINUX" == "true" ]]
    then
      if [[ "$MUSL" == "true" ]]
      then
        TARGET_ARG="musl"
      else
        TARGET_ARG="linux"
      fi
    fi
    echo ../configure --prefix=$INSTALLDIR/gnu $ARCH_ABI_ARGS $MULTILIB_ARGS "$MULTILIB_GEN_ARGS"
    ../configure --prefix=$INSTALLDIR/gnu $ARCH_ABI_ARGS $MULTILIB_ARGS "$MULTILIB_GEN_ARGS" 2>&1 | tee -a $LOGDIR/gcc.log
    make $TARGET_ARG -j`nproc` 2>&1 | tee -a $LOGDIR/gcc.log
    cd ../..

    # TODO: allow skipping gdb etc.
  fi

  if [[ "$ENABLE_LLVM" == "true" ]]
  then
    echo "Installing llvm ..."
    if [[ -d llvm ]]
    then
      echo "Skipping clone (already exists)"
    else
      echo git clone $LLVM_URL llvm 2>&1
      git clone $LLVM_URL llvm 2>&1 | tee -a $LOGDIR/llvm.log
      # git clone $LLVM_URL llvm --depth=1 2>&1 | tee -a $LOGDIR/llvm.log
    fi
    cd llvm
    if [[ "$LLVM_REF" != "" ]]
    then
      echo git checkout $LLVM_REF 2>&1
      git checkout $LLVM_REF 2>&1 | tee -a $LOGDIR/llvm.log
    fi
    # mkdir build
    # cd build
    cmake -B "$WORKDIR/llvm/build" "$WORKDIR/llvm/llvm/" -G $CMAKE_GENERATOR -DLLVM_ENABLE_PROJECTS="$LLVM_ENABLE_PROJECTS" "-DCMAKE_BUILD_TYPE=$CMAKE_BUILD_TYPE" -DCMAKE_INSTALL_PREFIX=$INSTALLDIR/llvm -DLLVM_TARGETS_TO_BUILD="$LLVM_TARGETS_TO_BUILD" -DLLVM_OPTIMIZED_TABLEGEN=$LLVM_OPTIMIZED_TABLEGEN -DLLVM_ENABLE_ASSERTIONS=$LLVM_ENABLE_ASSERTIONS -DLLVM_CCACHE_BUILD=$LLVM_CCACHE_BUILD -DLLVM_PARALLEL_LINK_JOBS=$LLVM_PARALLEL_LINK_JOBS -DLLVM_BUILD_TOOLS=$LLVM_BUILD_TOOLS -DLLVM_DEFAULT_TARGET_TRIPLE="$LLVM_DEFAULT_TARGET_TRIPLE" -DLLVM_ENABLE_ZSTD="$LLVM_ENABLE_ZSTD" 2>&1 | tee -a $LOGDIR/llvm.log

    cmake --build "$WORKDIR/llvm/build" -j`nproc` 2>&1 | tee -a $LOGDIR/llvm.log
    cmake --install "$WORKDIR/llvm/build" 2>&1 | tee -a $LOGDIR/llvm.log
    cd ..
  fi
  if [[ "$ENABLE_SPIKE" == "true" ]]
  then
    echo "Installing spike (riscv-isa-sim) ..."
    if [[ -d spike ]]
    then
      echo "Skipping clone (already exists)"
    else
      git clone $SPIKE_URL spike 2>&1 | tee -a $LOGDIR/spike.log
    fi
    cd spike
    if [[ "$SPIKE_REF" != "" ]]
    then
      git checkout $SPIKE_REF 2>&1 | tee -a $LOGDIR/spike.log
    fi
    mkdir -p build
    cd build
    # ../configure --prefix=$INSTALLDIR/spike
    ../configure --prefix=$INSTALLDIR/gnu 2>&1 | tee -a $LOGDIR/spike.log
    make -j`nproc` 2>&1 | tee -a $LOGDIR/spike.log
    mkdir -p $INSTALLDIR/spike
    cp spike $INSTALLDIR/spike/spike
    make install
    cd ../..
  fi
  if [[ "$ENABLE_PK" == "true" ]]
  then
    echo "Installing proxy kernel (riscv-pk) ..."
    if [[ -d pk ]]
    then
      echo "Skipping clone (already exists)"
    else
      git clone $PK_URL pk 2>&1 | tee -a $LOGDIR/pk.log
    fi
    cd pk
    if [[ "$PK_REF" != "" ]]
    then
      git checkout $PK_REF 2>&1 | tee -a $LOGDIR/pk.log
    fi
    mkdir -p build
    cd build
    if [[ ! -d $INSTALLDIR/gnu ]]
    then
      echo "Proxy kernel needs gnu installation!"
      exit 1
    fi
    export PATH=$INSTALLDIR/gnu/bin:$PATH
    HOST_ARGS=
    if [[ "$RISCV_HOST" != "" ]]
    then
      HOST_ARGS="$HOST_ARGS --host=$RISCV_HOST"
    fi
    ARCH_ABI_ARGS=
    if [[ "$ARCH" != "" ]]
    then
      ARCH_ABI_ARGS="$ARCH_ABI_ARGS --with-arch=$ARCH"
    fi
    ARCH_ABI_ARGS=
    if [[ "$ABI" != "" ]]
    then
      ARCH_ABI_ARGS="$ARCH_ABI_ARGS --with-abi=$ABI"
    fi
    ../configure --prefix=$INSTALLDIR/gnu $HOST_ARGS $ARCH_ABI_ARGS 2>&1 | tee -a $LOGDIR/pk.log
    make -j`nproc` 2>&1 | tee -a $LOGDIR/pk.log
    mkdir -p $INSTALLDIR/pk
    cp pk $INSTALLDIR/pk/pk
    make -j`nproc`
    make install 2>&1 | tee -a $LOGDIR/pk.log
  fi

  if [[ "$COMPRESS" == "true" ]]
  then
    echo "Compress!"
    # find $INSTALLDIR -mindepth 1 -maxdepth 1 -type d
    # echo find $INSTALLDIR -mindepth 1 -maxdepth 1 -type d -exec echo bash -c 'do_compress $@' {} $COMPRESS_EXT $COMPRESS_LEVEL $COMPRESS_KEEP \;
    find $INSTALLDIR -mindepth 1 -maxdepth 1 -type d -exec bash -c 'do_compress {} $0 $1 $2 $3' $COMPRESS_EXT $COMPRESS_LEVEL $COMPRESS_KEEP \;
  fi


  echo "Writing $INSTALLDIR/config.sh ..."
  echo "HOST=${HOST}" > $INSTALLDIR/config.sh
  echo "DEST=${DEST}" >> $INSTALLDIR/config.sh
  echo "VERBOSE=${VERBOSE}" >> $INSTALLDIR/config.sh
  echo "SETUP=${SETUP}" >> $INSTALLDIR/config.sh
  echo "LOGDIR=${LOGDIR}" >> $INSTALLDIR/config.sh
  echo "WORKDIR=${WORKDIR}" >> $INSTALLDIR/config.sh
  echo "COMPRESS=${COMPRESS}" >> $INSTALLDIR/config.sh
  echo "COMPRESS_EXT=${COMPRESS_EXT}" >> $INSTALLDIR/config.sh
  echo "COMPRESS_LEVEL=${COMPRESS_LEVEL}" >> $INSTALLDIR/config.sh
  echo "COMPRESS_KEEP=${COMPRESS_KEEP}" >> $INSTALLDIR/config.sh
  echo "FORCE=${FORCE}" >> $INSTALLDIR/config.sh
  echo "CLEANUP=${CLEANUP}" >> $INSTALLDIR/config.sh
  echo "ARCH=${ARCH}" >> $INSTALLDIR/config.sh
  echo "ABI=${ABI}" >> $INSTALLDIR/config.sh
  echo "CMODEL=${CMODEL}" >> $INSTALLDIR/config.sh
  echo "LINUX=${LINUX}" >> $INSTALLDIR/config.sh
  echo "MUSL=${MUSL}" >> $INSTALLDIR/config.sh
  echo "MULTILIB=${MULTILIB}" >> $INSTALLDIR/config.sh
  echo "MULTILIB_LARGE=${MULTILIB_LARGE}" >> $INSTALLDIR/config.sh
  echo "MULTILIB_DEFAULT_GENERATOR=${MULTILIB_DEFAULT_GENERATOR}" >> $INSTALLDIR/config.sh
  echo "MULTILIB_LARGE_GENERATOR=${MULTILIB_LARGE_GENERATOR}" >> $INSTALLDIR/config.sh
  echo "ENABLE_GCC=${ENABLE_GCC}" >> $INSTALLDIR/config.sh
  echo "ENABLE_SPIKE=${ENABLE_SPIKE}" >> $INSTALLDIR/config.sh
  echo "ENABLE_PK=${ENABLE_PK}" >> $INSTALLDIR/config.sh
  echo "ENABLE_LLVM=${ENABLE_LLVM}" >> $INSTALLDIR/config.sh
  echo "CMAKE_GENERATOR=${CMAKE_GENERATOR}" >> $INSTALLDIR/config.sh
  echo "GNU_URL=${GNU_URL}" >> $INSTALLDIR/config.sh
  echo "GNU_REF=${GNU_REF}" >> $INSTALLDIR/config.sh
  echo "GCC_URL=${GCC_URL}" >> $INSTALLDIR/config.sh
  echo "GCC_REF=${GCC_REF}" >> $INSTALLDIR/config.sh
  echo "BINUTILS_URL=${BINUTILS_URL}" >> $INSTALLDIR/config.sh
  echo "BINUTILS_REF=${BINUTILS_REF}" >> $INSTALLDIR/config.sh
  echo "LLVM_URL=${LLVM_URL}" >> $INSTALLDIR/config.sh
  echo "LLVM_REF=${LLVM_REF}" >> $INSTALLDIR/config.sh
  echo "SPIKE_URL=${SPIKE_URL}" >> $INSTALLDIR/config.sh
  echo "SPIKE_REF=${SPIKE_REF}" >> $INSTALLDIR/config.sh
  echo "PK_URL=${PK_URL}" >> $INSTALLDIR/config.sh
  echo "PK_REF=${PK_REF}" >> $INSTALLDIR/config.sh

  # Fix permissions
  chmod 644 -R $WORKDIR/install/
fi


echo "Copy to destination ..."
if [[ -d $DEST ]]
then
  echo "Destination already exists!"
  if [[ "$FORCE" == "true" ]]
  then
    rm -r $DEST
  else
    echo "(Use --force to overwrite)"
    exit 1
  fi
fi
mkdir -p $DEST
cp -r $WORKDIR/install/* $DEST/
# sudo chmod -R 777 $DEST/

if [[ "$CLEANUP" == "true" ]]
then
    rm -r $WORKDIR
    # sudo rm -r $WORKDIR
fi
