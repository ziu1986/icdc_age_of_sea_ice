# Compute multi-year sea ice cover fraction

> Author: Stefanie Falk (Stefanie.Falk@kit.edu)
> 
> Date: 2023-12-19

The python script `compute_my_sic_from_age.py` computes multi-year sea ice cover fractions based on the ICDC data set ("Sea-ice age for Arctic from NSIDC")[https://www.cen.uni-hamburg.de/en/icdc/data/cryosphere/seaiceage-arctic.html].

Data are available from 1984 and located at DKRZ/levante `/pool/data/ICDC/ice_and_snow/arctic_sea_ice_age/DATA/`. Requires DKRZ account!

For this purpose, the data which contains an estimated age of the sea ice (age distribution 1--~6 years) is split into first year sea ice (1,2] and multi-year sea ice (2,20).

Each grid cell in the ICDC data is only assigned with one particular age! After reaching its minimum extend in the beginning of September the age index is increased by one. Hence, a sudden shift from first-year to multi-year sea ice occurs.

Hence, for the purpose of computing fractional aged sea ice cover, each grid cell containing multi-year sea ice is assigned a value of 1, each cell containing first year sea ice is assigned a value of 0. (NANs are also set to zero).

Using the bash script `cdo_remap.sh` these data in regional polar-centric coordinates are remapped, e.g. conservatively, to a regular Gaussian grid, e.g. `T63` and missing values are set to 0, assuming all other regions do not contain multi-year sea ice.

## Installation
Download and install `miniconda` and run the following in your terminal session:

```bash
$ conda env create -f environment.yml
```

Activate the `conda` environment

```bash
$ conda activate mysic
```

## Usage
Use you can use either `ipython` once the environment is installed or execute the script from command line:

```bash
python3 ./compute_my_sic_from_age.py [examples/user_config.yml] [--debug --verbose --clean]
```

## For use in EMAC
Data should be merged along the time axis and monthly means computed. This can be easily achieved with `cdo`:

```bash 
cdo -s -O monmean -mergetime results/remapcon_multi_year_sic_nh_t43_20*  multi_year_sic_nh_t43_<first_year>0101_<last_year>1231_v4.1.nc
```

## TODO:
- [ ] Modularization
- [x] Use YML to steer the script
- [x] Put bash script into `tools` directory
- [x] Define a conda environment file to install a compatible cdo as well and use that in the bash script
- [x] Clean up and improve the plotting
- [x] Define debug option from command line