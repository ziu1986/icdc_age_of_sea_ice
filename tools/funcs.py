# Helper functions
# Author: Stefanie Falk (KIT)

import os, sys, glob, shutil
import argparse
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import datetime as dt
import yaml

def init():
    func_name = 'init'
    # Parse command line arguments
    parser = argparse.ArgumentParser(sys.argv)
    parser.add_argument(dest='config_file', nargs='?', default="examples/user_config.yml", help='Configuration file')
    parser.add_argument('-v', dest='verbose', action='store_true')
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.add_argument('--clean', dest='clean', action='store_true')
    args = parser.parse_args()
    print_msg(func_name, r"Loading configuration: %s" % args.config_file)
    # Read configuration
    with open(r'%s' % args.config_file) as file:
        config_list = yaml.load(file, Loader=yaml.FullLoader)
    file.close()
    return(config_list, args)

def print_msg(func_name, *message, **kwargs):
    mode = kwargs.get("mode", None)
    if mode=='debug':
        mode_str = "*debug*\n......"
    elif mode=='verbose':
        mode_str= "..."
    elif mode=='error':
        mode_str='ERROR:'
    else:
        mode_str= "-> "
    print("%s%s()" % (mode_str, func_name), *message)

def make_clean(dir_list):
    func_name = 'make_clean'
    print_msg(func_name, "Removing directories")
    for key in dir_list.keys():
        dir = dir_list[key]
        if os.path.exists(dir) and dir != '.':
            print_msg(func_name, dir)
            shutil.rmtree(dir)
    print_msg(func_name, "Done cleaning up.")

def make_dirs(dir_list, **kwargs):
    func_name = 'make_dirs'
    debug = kwargs.get('debug', False)
    for key in dir_list.keys():
        if not os.path.exists(dir_list[key]):
            if debug: print_msg(func_name, "Creating directory %s" % (dir_list[key]), mode=debug)
            os.makedirs(dir_list[key])
        else:
            if debug: print_msg(func_name, "Nothing to do.", mode=debug)

def read_data(*arg,**kwarg):
    func_name = 'read_data'
    # Get arguments
    infile = arg[0]
    input_dir = arg[1]

    data_list = []
    file_list = []
    if (infile.find('*')>=0) | (infile.find('?')>=0):
        for ifile in sorted(glob.glob(os.sep.join([input_dir, infile]))):
            file_list.append(os.path.basename(ifile))
            data_list.append(xr.open_dataset(ifile))
    elif (type(infile)==list):
        for ifile in sorted(infile):
            file_list.append(ifile)
            data_list.append(xr.open_dataset(os.sep.join([input_dir, ifile])))
    else:
        file_list.append(infile)
        data_list.append(xr.open_dataset(os.sep.join([input_dir, infile])))

    return(data_list, file_list)

def plot_icdc(*arg,**kwarg):
    func_name = 'plot_icdc'
    # Process function arguments
    data = arg[0]
    # Age >= 20 indicates land; 0 indicates ocean
    data_sel_ice = data.where((data.age_of_sea_ice>=1) & (data.age_of_sea_ice<20))
    # Plot it
    levels = np.arange(1,21)
    colors = ('darkblue', 'darkblue', 'darkblue',
              'blue', 'blue', 'blue',
              'darkgreen', 'darkgreen', 'darkgreen',
              'orange', 'orange', 'orange')
    markers = ('^', 's', 'o',
               '^', 's', 'o',
               '^', 's', 'o',
               '^', 's', 'o') 
    hist_list = []
    for imonth in np.arange(1,13):
        hist_list.append(data_sel_ice['age_of_sea_ice'].where(data_sel_ice['age_of_sea_ice'].time.dt.month.isin(imonth), drop=True).mean('time').plot.hist(bins=levels-0.5, histtype='step', label=imonth)[0])
    fig, ax = plt.subplots(1,2, figsize=(16,9))
    for imonth in np.arange(1,13):
        ax[0].plot(levels[:-1], hist_list[imonth-1], 
                   color=colors[imonth-1], fillstyle='none', marker=markers[imonth-1], ls=':',  
                   label=imonth)
    data_sel_ice['age_of_sea_ice'].isel(time=0).plot(ax=ax[1], levels=levels)
    ax[0].set_xticks(levels)
    ax[0].set_xlim(0,7)
    ax[0].legend()
    return(fig)

def plot_sic(*arg, **kwarg):
    func_name = 'plot_sic'
    # Process function arguments
    fy_sic = arg[0]
    my_sic = arg[1]

    # Plot it
    fig, ax2 = plt.subplots(1,3,figsize=(19,5))

    (fy_sic+my_sic).isel(time=0).plot(ax=ax2[0], cbar_kwargs={'label': "Sea ice cover"})
    fy_sic.isel(time=0).plot(ax=ax2[1], cbar_kwargs={'label': "First-year sea ice cover"})
    my_sic.isel(time=0).plot(ax=ax2[2], cbar_kwargs={'label': "Multi-year sea ice cover"})

    ax2[0].set_title("sea ice cover")
    ax2[1].set_title("First-year sea ice cover")
    ax2[2].set_title("Multi-year sea ice cover")

    return(fig)

def plot(*arg, **kwarg):
    func_name = 'plot'
    # Plot the remapping result
    data = arg[0]
    fysic = arg[1]
    mysic = arg[2]
    target = kwarg.pop('target', '.')
    debug = kwarg.pop('debug', False)
    verbose = kwarg.pop('verbose', False)
    interactive = kwarg.pop('interactive', False)
    prefix = kwarg.pop('fileprefix', '')

    if (verbose | debug):
        print_msg(func_name, "Saving plots", mode=verbose)

    # Clean up from previous execution
    plt.close('all')    
    fig1 = plot_icdc(data)
    fig2 = plot_sic(fysic, mysic)
    plt.tight_layout()
    # Show it
    if interactive:
        plt.show(block=False)
    else:
        fig1.savefig("%s" % os.sep.join([target, prefix+'sea_ice_age.png']))
        fig2.savefig("%s" % os.sep.join([target, prefix+'fy_my_sic.png']))
