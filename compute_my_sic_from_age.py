# Script to process sea ice age from ICDC database in Hamburg
# Compute multi-year sea ice concentrations for use with AirSnow
# Contact person: Stefan Kern (Uni Hamburg)
# Obs: Data is strongly biased towards older sea ice 
# Author: Stefanie Falk (KIT) - 2023-12-14

import os, sys
import xarray as xr
import datetime as dt
from tools.funcs import *

def main():
    # Configuration
    func_name = 'main'
    config, args = init()
    # YML
    input = config['input']
    tgt = config['target']
    nc_attrs = config['nc_attributes']
    infile = input['files']
    remapping_strategy = config['remapping']['strategy']
    remapping_resolution = config['remapping']['grid']
    # Command line parser
    verbose = args.verbose
    debug = args.debug
    clean = args.clean
    #-------------------------------------------------------------------
    # Clean up and exit
    if clean:
        make_clean(tgt)
        print_msg(func_name, " Exit.")
        return
    #-------------------------------------------------------------------
    # Create directory structure
    make_dirs(tgt, verbose=verbose, debug=debug)
    #-------------------------------------------------------------------
    # Check if we run interactively
    b_interactive = hasattr(sys, 'ps1')
    if verbose:
        if b_interactive:
            print_msg(func_name, "INFO: We are running from the interpreter! All plots will be shown in debug mode.", mode=verbose)
        else:
            print_msg(func_name, "INFO: We are running from the command line! All plots will be redirected to file in debug mode.", mode=verbose)

    # Load data
    data_list, file_list = read_data(infile, input['dir'])
    year_list = []
    # Loop over data
    for data, ifile in zip(data_list, file_list):
        print_msg(func_name, "Process file: %s" % (ifile))
        outfile = ifile.replace('iceage', 'multi_year_sic')
        # Get multi-year sea ice maps
        my_sic = xr.ones_like(data['age_of_sea_ice'])
        my_sic = my_sic.where((data.age_of_sea_ice>=2) & (data.age_of_sea_ice<20),0)

        year_list.append(dt.datetime.strptime(str(my_sic.time.min().to_numpy()), '%Y-%m-%d %H:%M:%S').date().year)
        print_msg(func_name, 'Year: ', year_list[-1], mode=debug)
        
        # Plot data
        if(debug):
            # Get first year sea ice maps
            fy_sic = xr.ones_like(data['age_of_sea_ice'])
            fy_sic = fy_sic.where((data.age_of_sea_ice>=1) & (data.age_of_sea_ice<2),0)
            plot(data, fy_sic, my_sic, 
                target=tgt['plots'], fileprefix=outfile.replace('.nc', '-'), 
                interactive=b_interactive, verbose=verbose, debug=debug)

        # Rename variable name and attributes
        my_sic = my_sic.rename('my_sic')

        for key in nc_attrs:
            if(debug):
                print(key, nc_attrs[key])
            my_sic.attrs[key] = nc_attrs[key]

        del my_sic.attrs['flag_values']

        # Prepare dataset
        data_new = data.copy().drop('age_of_sea_ice')
        data_new['my_sic'] = my_sic.astype(float)
        data_new = data_new.drop_vars(['latitude', 'longitude'])
        data_new = data_new.fillna(0)
        # Write dataset
        data_new.to_netcdf(os.sep.join([tgt['output'], outfile]))

        if debug:
            print(data_new)

        # Remap to lat-lon
        os.system('bash ./tools/cdo_remap.sh %s %s %s %s' % (remapping_strategy, os.sep.join([tgt['output'], outfile]), os.sep.join([tgt['output'], outfile.replace('12.5km', remapping_resolution)]), '%sgrid' % remapping_resolution))

    # Merge data along time axis and compute monthly mean
    if len(year_list) > 1:
        print_msg(func_name, "Merge data along time axis and compute monthly averages.", mode=verbose)
        merge_file = outfile.replace("12.5km", remapping_resolution).replace('%s0101' % year_list[-1], '%s0101' % year_list[0])
        print_msg(func_name, "Merged file: ", merge_file)
        os.system('cdo -s -O monmean -mergetime %s %s' % (os.sep.join([tgt['output'], '*~tmp']), os.sep.join([tgt['output'], merge_file])))
    else:
        # Rename temporary file
        os.system('mv %s %s' % (os.sep.join([tgt['output'], '*~tmp']), os.sep.join([tgt['output'], outfile.replace("12.5km", remapping_resolution)])))

    # Clean up results
    if not debug:
        print_msg(func_name, "Remove temporary files in results dir: ", tgt['output'], mode=debug)
        os.system('rm -r %s ' % (os.sep.join([tgt['output'], '*12.5km*'])))
        os.system('rm -rf %s ' % (os.sep.join([tgt['output'], '*~tmp'])))
    
    os.system('mv %s %s' % (os.sep.join([tgt['output'],'*']), os.sep.join([tgt['output'], "%s_%s01-%s12.nc" % (tgt['file'], year_list[0], year_list[-1])])))

    # Finish
    print_msg(func_name, " Finished.")

if __name__ == "__main__":
    main()
