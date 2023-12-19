#! /bin/bash
# Set up environment
source ~/bin/setpaths
use_conda
conda activate cdo

remapping=${1}
infile=${2}
outfile=${3}
res=${4}

echo "cdo_remap.sh"

if [[ -f ${outfile} ]]; then
    rm ${remapping}_${outfile}
fi

cdo -f nc -setmisstoc,0 -${remapping},${res} ${infile} ${remapping}_${outfile}
