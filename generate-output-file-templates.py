#!/usr/bin/python
#
# Prepare templates for output files from offline radiative transfer calculations
#   suitable for publishing on the Earth System Grid
#
# Robert Pincus, Robert.Pincus@colorado.edu, 2016-2017
#
# ---------------------------------------------------------------------------------
from netCDF4 import Dataset
import numpy as np
import time, uuid
# ---------------------------------------------------------------------------------
# Copy a variable and all its attributes from one netCDF file to another
#
def copyVar(nc_in, nc_out, name, newname=None) :
	if newname is None :
		newname = name
	nc_out.createVariable(newname, nc_in.variables[name].dtype, nc_in.variables[name].dimensions)
	nc_out.variables[newname].setncatts(nc_in.variables[name].__dict__)
	nc_out.variables[newname][:] = nc_in.variables[name][:]
# ---------------------------------------------------------------------------------

atmos_file = Dataset('multiple_input4MIPs_radiation_RFMIP_UColorado-RFMIP-1-1_none.nc', mode='r')
# Available from https://www.earthsystemcog.org/projects/rfmip/resources/
# or from https://esgf-node.llnl.gov/search/input4mips/ ; search for "RFMIP"

#
# Model/institution specific attributes - replace these with values suitable for your institution, model, etc.
#
institution_id = "AER"
source_id      = "LBLRTM-12-8"
physics_index = np.int32(1)  # Use, e.g. for different approximations
forcing_index = np.int32(1)  # This values follows page 2074 in https://dx.doi.org/10.5194/gmd-10-2057-2017
                   # 1 = calculations uses all available greenhouse gases
                   # 2 = calculation uses CO2, CH4, N2O, CFC11eq
                   # 3 = calculation uses CO2, CH4, N2O, CFC12eq, HFC-134eq
variant_label  = "r1i1p{0}f{1}".format(physics_index,forcing_index)
model_attrs = {
  "institution_id"  :"AER",
  "institution"     :"Research and Climate Group, Atmospheric and Environmental Research, 131 Hartwell Avenue, Lexington, MA 02421, USA",
  "source_id"       :source_id,
  "version"         :"12.8",
  "source"          :"LBLRTM 12.8 (2017): \naerosol: none\natmos: none\natmosChem: none\nland: none\nlandIce: none\nocean: none\nocnBgchem: none\nseaIce: none",
                     # Needs to match entry for source_id in CMIP6 controlled vocabulary
  "further_info_url":"https://furtherinfo.es-doc.org/CMIP6." + institution_id + "." + source_id + ".rad-irf.none." + variant_label,
  "forcing_index"   :np.int32(forcing_index),
  "license"         :"CMIP6 model data produced by " + institution_id + " is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (https://creativecommons.org/licenses). " +
                     "Consult https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use governing CMIP6 output, including citation requirements and proper acknowledgment. " +
                     "Further information about this data, including some limitations, can be found via the further_info_url (recorded as a global attribute in this file) and at https://pcmdi.llnl.gov/." +
                     "The data producers and data providers make no warranty, either express or implied, including, but not limited to, warranties of merchantability and fitness for a particular purpose." +
                     "All liabilities arising from the supply of the information (including any liability arising in negligence) are excluded to the fullest extent permitted by law." }

#
# Required attributes, uniform across submissions
#
std_attrs = {
  "data_specs_version":"01.00.29",
  "physics_index":int(physics_index)}

# Submission attrs
sub_attrs = {
  'creation_date':time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
  'tracking_id'  : '/'.join(['hdl:21.14100',str(uuid.uuid4())]),
  "variant_label":variant_label}

# Attributes are taken from https://docs.google.com/document/d/1h0r8RZr_f3-8egBMMh7aqLwy3snpD6_MrDz1q8n5XUk/edit
# Data reference syntax attributes
drs_attrs = {
  "activity_id"  :"RFMIP",   # (from CMIP6_activity_id.json)
  "product"      :"model-output",
  "experiment_id":"rad-irf", # (from CMIP6_experiment_id.json)
  "table_id"     :"Efx",     # (per http://clipc-services.ceda.ac.uk/dreq/u/efc0de22-5629-11e6-9079-ac72891c3257.html)
  "frequency"    :"fx",
  "sub_experiment_id":"none"}

expt_attrs = {
  "Conventions"         :"CF-1.7 CMIP-6.2",
  "mip_era"             :"CMIP6",
  "experiment"          :"rad_irf",
  "sub_experiment"      :"none",
  "product"             :"model-output",
  "realization_index"   :np.int32(1),
  "initialization_index":np.int32(1),
  "source_type"         :"RAD",
  "nominal_resolution"  :"10 km",
  "realm"               :"atmos",
  "grid_label"          :"gn",
  "grid"                :"columns sampled from ERA-Interim, radiative fluxes computed independently"}

short_names = ['rlu','rsu', 'rld', 'rsd']
stand_names = ['upwelling_longwave_flux_in_air','upwelling_shortwave_flux_in_air',
               'downwelling_longwave_flux_in_air','downwelling_shortwave_flux_in_air']

for short, std in zip(short_names, stand_names) :
    out_file_name = short + ".nc"
    print('Creating ' + out_file_name)
    out_file = Dataset(out_file_name, mode='w', FORMAT='NETCDF4_CLASSIC')
    out_file.setncatts(drs_attrs)
    out_file.setncatts(std_attrs)
    out_file.setncatts(expt_attrs)
    out_file.setncatts(model_attrs)
    out_file.setncatts(sub_attrs)
    out_file.setncatts({'variable_id'  :short})
    d = out_file.createDimension('expt',  atmos_file.dimensions['expt'].size)
    d = out_file.createDimension('site',  atmos_file.dimensions['site'].size)
    d = out_file.createDimension('level', atmos_file.dimensions['level'].size)
    copyVar(atmos_file, out_file, 'lat')
    copyVar(atmos_file, out_file, 'lon')
    copyVar(atmos_file, out_file, 'time')
    copyVar(atmos_file, out_file, 'pres_level', 'plev')
    v = out_file.createVariable(short,   'f4', ('expt', 'site', 'level'))
    v.setncatts({'variable_id'  :short,
                 'standard_name':std,
                 'units'        :'W m-2',
                 'coordinates'  :'lon lat time'})
    copyVar(atmos_file, out_file, 'profile_weight')
    out_file.close()
