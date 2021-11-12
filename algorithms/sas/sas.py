def main(
    data,
    params,
    sf_params,
    options,
    **kwargs
): 
    from copy import deepcopy

    import sasmodels as sm
    import sasmodels.data
    import sasmodels.core
    import sasmodels.bumps_model
    from sas.sascalc.dataloader.data_info import Data1D

    import bumps.fitproblem
    import bumps.fitters
    from bumps.options import FIT_CONFIG

    import numpy as np
    import pandas as pd

    from opendatafit.lib import sas
    from opendatafit.lib.dataframe import ODFDataFrame

    from frictionless import Resource, Package

    # Load data as sasview Data1D object
    sasdata = Data1D.from_resource(data.get_resource("data"))

    # TODO: Setting beamstop breaks dataset construction as X doesn't match 
    # fitted data - fix this via to_masked_array maybe??
    #sm.data.set_beam_stop(sasdata, 0.008, 0.19)

    # Get selected model name
    options = options.get_resource("options")  # Temporary hack...
    model_name = options.get_option("model")
    sf_name = options.get_option("structureFactor")

    if sf_name:
        load_name = model_name+"@"+sf_name
    else:
        load_name = model_name

    kernel = sm.core.load_model(load_name)

    # Initialise model
    # TODO: Error handling for if no params are set to "vary" - bumps fails 
    # non gracefully on this

    # Get form factor and polydispersity params
    model_params = params.get_resource(model_name)
    combined_model_params = model_params

    # Add structure factor model params if selected
    # TODO: TEST THIS WORKS
    if sf_name:
        sf_model_params = sf_params.get_resource(sf_name)
        combined_model_params.concat(sf_model_params)

    if kwargs.get('plot_only', False):
        # Don't fit if plot_only flag set
        run_fit = False
    else:
        # Are there any parameters to be fitted?
        # (checks if any parameters are set to "vary")
        run_fit = np.any(list(combined_model_params.get_values(field="vary").values()))

    # Create bumps model
    model = sas.parameter_resource_to_bumps_model(kernel, combined_model_params)

    # Set up bumps fitter
    M = sm.bumps_model.Experiment(data=sasdata, model=model)
    problem = bumps.fitproblem.FitProblem(M)

    # Set bumps to use selected fitter method
    fitter_name = options.get_option("method")
    FIT_CONFIG.selected_id = getattr(bumps.fitters, fitter_name).id

    fitter = FIT_CONFIG.selected_fitter
    fitter_options =  FIT_CONFIG.selected_values

    # Set up fitter and run
    fitdriver = bumps.fitters.FitDriver(fitter, problem=problem, **fitter_options)

    if run_fit:
        best, fbest = fitdriver.fit()

    # Build fit curve resource
    # TODO: CHECK CONVERGENCE
    # (test by setting initial params to something bad - theory() returns NaNs)
    fit_df = pd.DataFrame(data={
        'x':         problem.fitness._data.x.flatten(),
        'y':         problem.fitness.theory().flatten(),
        'residuals': problem.fitness.residuals().flatten(),
    })

    fit_table = Resource(
        fit_df,
        name="fit",
        format="pandas",
        schema={
            'primaryKey': 'x',
            'fields': [
                {
                    'name': 'x',
                    'type': 'number',
                    'title': sasdata._xaxis,
                    'unit': sasdata._xunit,
                },
                {
                    'name': 'y',
                    'type': 'number',
                    'title': sasdata._yaxis,
                    'unit': sasdata._yunit,
                },
                {
                    'name': 'residuals',
                    'type': 'number',
                    'title': sasdata._yaxis,
                    'unit': sasdata._yunit,
                },
            ]
        }
    )

    fit_pkg.resources = [fit_table, *data.resources]

    # Optimised parameter resources
    fit_model_params = sas.bumps_model_to_parameter_resource(model, model_params)
    fit_model_params_pkg = Package(resources=[fit_model_params])
    # TODO: TEMP HACK
    fit_model_params_pkg["views"] = params["views"]

    fit_model_sf_params_pkg = Package()
    if sf_name:
        fit_model_sf_params = sas.bumps_model_to_parameter_resource(model, sf_model_params)
        fit_model_sf_params_pkg.resources = [fit_model_sf_params]
        # TODO: TEMP HACK
        fit_model_sf_params_pkg["views"] = sf_params["views"]

    return {
      'result_fit': fit_pkg,
      'result_params': fit_model_params_pkg,
      'result_sf_params': fit_model_sf_params_pkg,
    }

