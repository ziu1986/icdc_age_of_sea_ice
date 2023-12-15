#! /bin/bash
# Set up environment
source ~/bin/setpaths
use_conda
conda activate cdo

infile=${1}
outfile=${2}
res=${3}

echo "cdo_remap.sh"

if [[ -f ${outfile} ]]; then
    rm ${outfile}
fi

cdo -f nc remapcon,${res} ${infile} ${outfile}
