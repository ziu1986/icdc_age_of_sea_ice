#! /bin/bash
# This script uses cdo to remap and extend the NH polar projection 
# and sets all other grid cells to 0 globally

remapping=${1}
infile=${2}
outfile=${3}
res=${4}

echo "cdo_remap.sh"

if [[ -f ${outfile} ]]; then
    rm ${remapping}_${outfile}
fi

cdo -f nc -setmisstoc,0 -${remapping},${res} ${infile} ${remapping}_${outfile}
