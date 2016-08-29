"""Collection of functions for dealing with grids.

Functions:
  curvilinear_to_rectilinear  -- Regrid curvilinear data to a rectilinear 
                                 grid if necessary

"""

import pdb
import numpy
import iris
from iris.experimental.regrid import regrid_weighted_curvilinear_to_rectilinear


def _check_coord_names(cube, coord_names):
    """Remove specified coordinate name.

    The iris standard names for lat/lon coordinates are:
      latitude, grid_latitude, longitude, grid_longitude

    If a cube uses one for the dimension coordinate and the 
      other for the auxillary coordinate, the 
      regrid_weighted_curvilinear_to_rectilinear method won't work

    Args:
      cube (iris.cube.Cube)
      coord_names(list)

    """

    if 'grid_latitude' in coord_names:
        cube.coord('grid_latitude').standard_name = None
        coord_names = [coord.name() for coord in cube.dim_coords]
    if 'grid_longitude' in coord_names:
        cube.coord('grid_longitude').standard_name = None
        coord_names = [coord.name() for coord in cube.dim_coords]

    return cube, coord_names


def _make_grid(lat_values, lon_values):
    """Make a dummy cube with desired grid."""
       
    latitude = iris.coords.DimCoord(lat_values,
                                    standard_name='latitude',
                                    units='degrees_north',
                                    coord_system=None)
    longitude = iris.coords.DimCoord(lon_values,                    
                                     standard_name='longitude',
                                     units='degrees_east',
                                     coord_system=None)

    dummy_data = numpy.zeros((len(lat_values), len(lon_values)))
    new_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    new_cube.coord('longitude').guess_bounds()
    new_cube.coord('latitude').guess_bounds()

    return new_cube


def curvilinear_to_rectilinear(cube):
    """Regrid curvilinear data to a rectilinear grid if necessary."""

    coord_names = [coord.name() for coord in cube.dim_coords]
    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    
    if 'time' in aux_coord_names:
        aux_coord_names.remove('time')

    if aux_coord_names == ['latitude', 'longitude']:

        # Create target grid
        lats = numpy.arange(-90, 91, 1)
        lons = numpy.arange(0, 360, 1)
        target_grid_cube = _make_grid(lats, lons)

        # Interate over slices (experimental regridder only works on 2D slices)
        cube, coord_names = _check_coord_names(cube, coord_names)
        slice_dims = coord_names

        if 'time' in slice_dims:
            slice_dims.remove('time')
        if 'depth' in slice_dims:
            slice_dims.remove('depth')
    
        cube_list = []
        for i, cube_slice in enumerate(cube.slices(slice_dims)):
            weights = numpy.ones(cube_slice.shape)
            regridded_cube = regrid_weighted_curvilinear_to_rectilinear(cube_slice, weights, target_grid_cube)
            cube_list.append(regridded_cube)

        new_cube = iris.cube.CubeList(cube_list)
        new_cube = new_cube.merge_cube()
        coord_names = [coord.name() for coord in new_cube.dim_coords]

    else:

        new_cube = cube
    
    return new_cube, coord_names


