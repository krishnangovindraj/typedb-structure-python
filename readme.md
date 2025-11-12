# TypeDB graph visualiser tutorial (Python)

## Install from source:
1. Ensure you have build
   * `python3 -m pip install build` 
2. Build (creates files under dist/) 
   * `python3 -m build` # Creates files under dist/
3. Install from the wheel created in the previous step:
   * `python3 -m pip install dist/typedb_graph_visualizer_example-0.0.1-py3-none-any.whl`

## Testing
You don't have to "install from source".
1. Manually install the library dependencies
   * `python3 -m pip install -e .`
2. Manually install the dev dependencies 
   * `python3 -m pip install -e '.[dev]'`
3. Run tests:
   * `python3 -m pytest` 

## Run the sample
I created a 'main' in the tests file to visualise the graphs created by the tests. Run it:
`python3 -m test.test_simple`
