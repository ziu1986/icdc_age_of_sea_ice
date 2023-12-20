# Script to plot sea ice age from ICDC database in Hamburg
# Contact person: Stefan Kern (Uni Hamburg)
# Obs: Data is strongly biased towards older sea ice 
# Author: Stefanie Falk (KIT) - 2023-12-14

import os, sys, glob
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import yaml


def init(config_file):
    # Read configuration
    with open(r'%s' % config_file) as file:
        config_list = yaml.load(file, Loader=yaml.FullLoader)
    file.close()
    return(config_list)

def plot_icdc(*arg,**kwarg):
    # Process function arguments
    data = arg[0]
    # Age >= 20 indicates land; 0 indicates ocean
    data_sel_ice = data.where(data.age_of_sea_ice<20)
    # Plot it
    fig, ax = plt.subplots(2,2, figsize=(16,9))
    data_sel_ice['age_of_sea_ice'].isel(time=0).plot(ax=ax[0,0])
    data_sel_ice['age_of_sea_ice'].plot.hist(ax=ax[0,1], bins=21)
    data_sel_ice['age_of_sea_ice'].where((data.age_of_sea_ice<=1) & (data.age_of_sea_ice>0)).isel(time=0).plot(ax=ax[1,0])
    data_sel_ice['age_of_sea_ice'].where(data.age_of_sea_ice>1).isel(time=0).plot(ax=ax[1,1])
    # Set axis titles
    ax[1,0].set_title("First-year sea ice")
    ax[1,1].set_title("Multi-year sea ice")

    return(fig)

def plot_sic(*arg, **kwarg):
    # Process function arguments
    fy_sic = arg[0]
    my_sic = arg[1]

    # Plot it
    fig, ax2 = plt.subplots(1,3,figsize=(19,5))

    (fy_sic+my_sic).isel(time=0).plot(ax=ax2[2], cbar_kwargs={'label': "Sea ice cover"})
    fy_sic.isel(time=0).plot(ax=ax2[0], cbar_kwargs={'label': "First-year sea ice cover"})
    my_sic.isel(time=0).plot(ax=ax2[1], cbar_kwargs={'label': "Multi-year sea ice cover"})

    ax2[0].set_title("sea ice cover")
    ax2[1].set_title("First-year sea ice cover")
    ax2[2].set_title("Multi-year sea ice cover")

    return(fig)

def plot_mysic_result(*arg, **keyarg):
    # Plot the remapping result

def main():
    
    b_debug = True
    b_interactive = hasattr(sys, 'ps1')

    if b_interactive:
        print("INFO: We are running from the interpreter! All plots will be shown in debug mode.")
    else:
        print("INFO: We are running from the command line! All plots will be redirected to file in debug mode.")   
    
    # Read configuration
    config = init("config.yml")
    src = config['directories']['input']
    tgt = config['directories']['output']
    plotdir = config['directories']['plots']
    nc_attrs = config['nc_attributes']
    infile = config['files']['input']
    outfile = infile.replace('iceage', 'multi_year_sic')
    remapping_strategy = config['remapping']['strategy']
    remapping_resolution = config['remapping']['grid']

    # Load data
    data = xr.open_dataset(os.sep.join([src, infile]))

    # Get multi-year sea ice maps
    my_sic = xr.ones_like(data['age_of_sea_ice'])
    my_sic = my_sic.where((data.age_of_sea_ice>1) & (data.age_of_sea_ice<20),0)

    # Plot data
    if(b_debug):
        # Clean up from previous execution
        plt.close('all')
        # Get first year sea ice maps
        fy_sic = xr.ones_like(data['age_of_sea_ice'])
        fy_sic = fy_sic.where((data.age_of_sea_ice>0) & (data.age_of_sea_ice<=1),0)
    
        fig1 = plot_icdc(data)
        fig2 = plot_sic(fy_sic, my_sic)
        # Show it
        if b_interactive:
            plt.show(block=False)
        else:
            if not os.path.isdir(plotdir):
                os.mkdir(plotdir)
            fig1.savefig("%s" % os.sep.join([plotdir, 'sea_ice_age.png']))
            fig2.savefig("%s" % os.sep.join([plotdir, 'fy_my_sic.png']))

    # Rename variable name and attributes
    my_sic = my_sic.rename('my_sic')

    for key in nc_attrs:
        if(b_debug):
            print(key, nc_attrs[key])
        my_sic.attrs[key] = nc_attrs[key]

    del my_sic.attrs['flag_values']

    # Prepare dataset
    data_new = data.copy().drop('age_of_sea_ice')
    data_new['my_sic'] = my_sic.astype(float)
    data_new = data_new.drop_vars(['latitude', 'longitude'])
    data_new = data_new.fillna(0)
    # Write dataset
    data_new.to_netcdf(os.sep.join([tgt, outfile]))

    if b_debug:
        print(data_new)

    # Remap to lat-lon
    os.system('bash ./tools/cdo_remap.sh %s %s %s %s' % (remapping_strategy, os.sep.join([tgt, outfile]), os.sep.join([tgt, outfile.replace('12.5km', remapping_resolution)]), '%sgrid' % remapping_resolution))
        
if __name__ == "__main__":
    main()
