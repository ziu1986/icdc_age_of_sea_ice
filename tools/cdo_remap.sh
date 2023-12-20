#! /bin/bash
# This script uses cdo to remap and extend the NH polar projection 
# and sets all other grid cells to 0 globally

remapping=${1}
infile=${2}
outfile=${3}
res=${4}

outfile_name=`basename ${outfile}`
outfile_dir=`dirname ${outfile}`

echo "bash -> cdo_remap.sh"

if [[ -f ${outfile_dir}/${remapping}_${outfile} ]]; then
    rm ${outfile_dir}/${remapping}_${outfile}
fi

cdo -f nc -setmisstoc,0 -${remapping},${res} ${infile} ${outfile_dir}/${remapping}_${outfile_name}

