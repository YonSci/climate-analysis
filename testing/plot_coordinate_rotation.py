"""
A testing module for visualising coordinate system rotation.

Functions/methods tested:
  coordinate_rotation.switch_regular_axes

"""
import os, sys

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import coordinate_rotation as rot

module_dir2 = os.path.join(os.environ['HOME'], 'visualisation')
sys.path.insert(0, module_dir2)
import plot_map

import numpy
import cdms2

import pdb

##############
## plotting ##
##############        

def create_latlon_dataset(res=2.5):
    """Create a dataset corresponding to the latitude (output 1) and
    longitude (output 2) of each grid point"""

    nlats = int((180.0 / res) + 1)
    nlons = int(360.0 / res)
    grid = cdms2.createUniformGrid(-90.0, nlats, res, 0.0, nlons, res)
    
    lat_data = numpy.zeros([nlats, nlons])
    lat_axis = numpy.arange(-90, 90 + res, res)
    for index in range(0, nlats):
        lat_data[index, :] = lat_axis[index]
    lat_data_cdms = cdms2.createVariable(lat_data[:], grid=grid)

    lon_data = numpy.zeros([nlats, nlons])
    lon_axis1 = numpy.arange(0, 180 + res, res)
    lon_axis2 = numpy.arange(180 - res, 0, -res)
    for index in range(0, len(lon_axis1)):
        lon_data[:, index] = lon_axis1[index]
    for index in range(0, len(lon_axis2)):
	lon_data[:, index + len(lon_axis1)] = lon_axis2[index]
    lon_data_cdms = cdms2.createVariable(lon_data[:], grid=grid)

    return lat_data_cdms, lon_data_cdms


def switch_and_restore(data, new_np):
    """Test the switch_axes function"""

    lat_axis = data.getLatitude()
    lon_axis = data.getLongitude()
    
    rotated_data = rot.switch_regular_axes(data, lat_axis[:], lon_axis[:], new_np, invert=False)
    cdms_rotated_data = cdms2.createVariable(rotated_data[:], axes=[lat_axis, lon_axis])

    returned_data = rot.switch_regular_axes(rotated_data, lat_axis[:], lon_axis[:], new_np, invert=True)
    cdms_returned_data = cdms2.createVariable(returned_data[:], axes=[lat_axis, lon_axis])

    return cdms_rotated_data, cdms_returned_data
    

def plot_axis_switch(new_np):
    """Plot the original, rotated and returned data"""

    orig_lat_data, orig_lon_data = create_latlon_dataset()
    rotated_lat_data, returned_lat_data = switch_and_restore(orig_lat_data, new_np)
    rotated_lon_data, returned_lon_data = switch_and_restore(orig_lon_data, new_np)

    title = 'Axis switch for new NP at %sN, %sE' %(str(new_np[0]), str(new_np[1])) 

    # Latitude plot
    plot_lat_list = [orig_lat_data, rotated_lat_data, returned_lat_data]
    plot_map.multiplot(plot_lat_list,
                       dimensions=(3, 1),  
                       title=title,
                       ofile='axis_switch_lat_%sN_%sE.png' %(str(new_np[0]), str(new_np[1])), 
                       row_headings=['original', 'rotated', 'returned'],
                       draw_axis=True, delat=15, delon=30, equator=True)

    # Longitude plot

if __name__ == '__main__':
    plot_axis_switch([0, 0])
