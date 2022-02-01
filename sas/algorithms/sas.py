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
    from sas.sascalc.dataloader.loader import Loader

    import bumps.fitproblem
    import bumps.fitters
    from bumps.options import FIT_CONFIG

    import numpy as np
    import pandas as pd

    from frictionless import Resource, Package

    import base64
    import io

    import tempfile


    # =========================================================================
    # General helpers

    def find(lst, key, value):
        # Return item item matching i[key] == value in a list of dicts
        for dic in lst:
            if dic[key] == value:
                return dic
        return None


    # =========================================================================
    # SAS helpers


    def parameter_resource_to_bumps_model(kernel, resource):
        # TODO: Need a way to include/exclude PD parameters depending on option
        # selection...

        params = resource.get_values()
        model = sm.bumps_model.Model(kernel, **params)

        for key, param in resource.data.items():
            if type((getattr(model, key))) == bumps.parameter.Parameter:
                vary = param.get("vary", None)
                if vary is not None:
                    if vary:
                        # (this also sets fixed=False in bumps)
                        getattr(model, key).limits = (
                            param["lowerBound"],
                            param["upperBound"],
                        )
                        getattr(model, key).fixed = False
                    else:
                        getattr(model, key).fixed = True

        return model


    def bumps_model_to_parameter_resource(model, params):
        """
        " params: frictionless.Resource
        " model: sasmodels.bumps_model.Model
        "
        " Updates params resource with fitted parameters from bumps model
        """

        # bumps_model.Model class is a wrapper around sasview_model.Model,
        # containing fitting information on top of model definition

        for param in params.get_values().keys():
            params.set_param(
                key=param,
                value=model.state()[param],
                field="value",
            )

        return params


    # =========================================================================
    # Extended Resource classes


    class ParameterResource(Resource):
        def concat(self, resource):
            # Check profiles match
            assert self.profile == resource.profile

            # Concat schema
            # TODO: Match any identical descriptors in schema?
            # TODO: Implement custom ParameterSchema object
            keys = self.schema.to_dict()["keys"]
            keys.append(resource.schema.to_dict()["keys"])
            self.schema["keys"] = keys

            # Concat data
            self.data.update(resource.data)

        def get_param(self, key, field=None):
            if field is not None:
                return self.data[key][field]
            else:
                return self.data[key]

        def set_param(self, key, value, field=None):
            if field is not None:
                self.data[key][field] = value
            else:
                self.data[key] = value

        def get_values(self, field="value"):
            # TODO: Handle non-float values!

            def is_float(value):
                try:
                    float(value)
                    return True
                except:  # noqa: E722
                    return False

            return {
                key: float(row.get(field))
                if is_float(row.get(field))
                else row.get(field)
                for key, row in self.data.items()
            }

        def add_field(self, key, name, **kwargs):
            # TODO: Test this works
            key_schema = find(self.schema["keys"], "name", key)
            key_schema["fields"].append({"name": name, **kwargs})


    class OptionsResource(Resource):
        def get_option(self, option):
            return self.data[option]["name"]

        def set_option(self, option, key):
            self.data[option] = self.get_option_choice(option, key)

        def get_option_choice(self, option, key):
            field = find(self.schema.fields, "name", option)
            return find(field["constraints"]["enum"], "name", key)


    class FileResource(Resource):
        @property
        def file(self):
            return io.BytesIO(base64.b64decode(self.data))

        @property
        def file_name(self):
            return self.title.rsplit(".", 1)[0]

        @property
        def file_ext(self):
            return self.title.rsplit(".", 1)[1]


    # =========================================================================
    # Analysis algorithm

    data_resource = FileResource(descriptor=data)

    # Write to temporary file for reading by SASView
    # TODO: Would be ideal not to have to do this...
    with tempfile.NamedTemporaryFile(
            dir="/tmp",
            prefix=data_resource.file_name+"_",
            suffix="."+data_resource.file_ext) as f:

        # Create temporary file to be loaded by sasview
        f.write(data_resource.file.getbuffer())

        loader = Loader()

        # TODO: Handle multiple return Data objs - example file for this case?
        # TODO: Handle Data2D case
        data_sas = loader.load(f.name)
        data_sas = data_sas[0]

    print("==================================================")
    print("Got SAS data:")
    print(data_sas)
    print("==================================================")

    # TODO: Setting beamstop breaks dataset construction as X doesn't match 
    # fitted data - fix this via to_masked_array maybe??
    # sm.data.set_beam_stop(data_sas, 0.008, 0.19)

    # TODO: TEMP
    # Convert options JSON into Resource
    options_resource = OptionsResource(descriptor=options)

    # Get selected model name
    model_name = options_resource.get_option("model")
    sf_name = options_resource.get_option("structureFactor")

    if sf_name:
        load_name = model_name+"@"+sf_name
    else:
        load_name = model_name

    kernel = sm.core.load_model(load_name)

    # Initialise model
    # TODO: Error handling for if no params are set to "vary" - bumps fails 
    # non gracefully on this

    # TODO: TEMP
    # Convert params JSON into Resource
    params_resource = ParameterResource(descriptor=params)
    # TODO: TEMP gross, used below to convert bumps results to resources
    model_params = params_resource
    if sf_params is not None:
        sf_params_resource = ParameterResource(descriptor=sf_params)
        # TODO: TEMP gross, used below to convert bumps results to resources
        sf_model_params = sf_params_resource

    # Combine form factor/polydispersity params with SF params
    params_resource.concat(sf_params_resource)

    if kwargs.get('plot_only', False):
        # Don't fit if plot_only flag set
        run_fit = False
    else:
        # Are there any parameters to be fitted?
        # (checks if any parameters are set to "vary")
        run_fit = np.any(list(params_resource.get_values(field="vary").values()))

    # Create bumps model
    model = parameter_resource_to_bumps_model(kernel, params_resource)

    # Set up bumps fitter
    M = sm.bumps_model.Experiment(data=data_sas, model=model)
    problem = bumps.fitproblem.FitProblem(M)

    # Set bumps to use selected fitter method
    fitter_name = options_resource.get_option("method")
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
                    'title': data_sas._xaxis,
                    'unit': data_sas._xunit,
                },
                {
                    'name': 'y',
                    'type': 'number',
                    'title': data_sas._yaxis,
                    'unit': data_sas._yunit,
                },
                {
                    'name': 'residuals',
                    'type': 'number',
                    'title': data_sas._yaxis,
                    'unit': data_sas._yunit,
                },
            ]
        }
    )

    # TODO: Old Pandas encoder - should we use this instead?
    # See: datafit-framework -> pipeline/framework/datatypes/package.py

    # class PandasJSONEncoder(json.JSONEncoder):
    #     def default(self, obj):
    #         """
    #         " Convert Pandas dataframes to json
    #         """
    #         if type(obj) == pd.DataFrame:
    #             # Return dataframe as list of keyed rows
    #             return obj.to_dict("records")

    #         return super().default(obj)

    # TODO: TEMP
    # Convert data from Pandas DataFrame to JSON rows for serialization
    rows = fit_table.data.to_dict("records")
    fit_table.data = rows

    # Optimised parameter resources
    fit_model_params = bumps_model_to_parameter_resource(model, model_params)

    if sf_name:
        fit_model_sf_params = bumps_model_to_parameter_resource(model, sf_model_params)

    return {
      'result_fit': fit_table,
      'result_params': fit_model_params,
      'result_sf_params': fit_model_sf_params,
    }

