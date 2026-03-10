#!/bin/bash
ENV PROJ_HOME=$PWD
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1
ENV JULIA_VERSION="1.11.5"
ENV POETRY_VERSION="2.1.3"
ENV PYTHONUNBUFFERED=1
ENV PATH="$HOME/.local/bin:$PATH"
ENV PYTHONPATH=$PWD

echo "Start installing dependencies..."
echo $PROJ_HOME
echo "Installing Solvers(GLPK, IPOPT, HIGHS)"
apt-get update && apt-get install -y curl
# GLPK
apt-get install -y libglpk-dev glpk-utils
glpsol --version
apt-get install -y gfortran  gcc  g++  make  wget  unzip  pkg-config  liblapack-dev  libblas-dev  libtool  coinor-libipopt-dev  build-essential  git  cmake  python3-dev  python3-pip  libopenblas-dev  libmumps-seq-dev  libmetis-dev
# Highs
cd /opt
mkdir highs && cd highs
git clone https://github.com/ERGO-Code/HiGHS.git && cd HiGHS
cmake -S . -B build
cmake --build build
cd build && ctest
PATH=$PATH:/opt/highs/HiGHS/build/bin
# Julia
echo "Installing Julia"
cd /tmp
wget https://julialang-s3.julialang.org/bin/linux/x64/${JULIA_VERSION:0:4}/julia-$JULIA_VERSION-linux-x86_64.tar.gz
tar -xzf julia-$JULIA_VERSION-linux-x86_64.tar.gz
mv julia-$JULIA_VERSION /opt/julia
ln -s /opt/julia/bin/julia /usr/bin/julia
julia --version
cd $PROJ_HOME
julia --project=./src/service/optimization_service/julia -e "import Pkg; Pkg.instantiate()"

# Poetry
echo "Installing Poetry"
cd $PROJ_HOME
echo $PROJ_HOME
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
poetry install --no-interaction  --no-ansi --no-root
export PYTHONPATH=$PWD

echo "export LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:/usr/local/lib\"" >> /etc/profile.d/myenv.sh
echo "export PATH=\"$PATH:/opt/highs/HiGHS/build/bin:$HOME/.local/bin\"" >> /etc/profile.d/myenv.sh
echo "export PYTHONPATH=$PWD" >> /etc/profile.d/myenv.sh