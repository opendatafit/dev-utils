# dev-utils

## Scripts

### generate_js.py

```
./generate_js.py sas_datapackage sas/datapackage.json
```

Will generate the following file ```js/sas_datapackage.js```:
```
const SAS_DATAPACKAGE = {
  // datapackage content here
};

export { SAS_DATAPACKAGE };
```
