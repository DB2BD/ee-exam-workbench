import importlib.util, pathlib
_p = pathlib.Path(__file__).with_name('EE-114-01-2_common.py')
_s = importlib.util.spec_from_file_location('c', _p); c = importlib.util.module_from_spec(_s); _s.loader.exec_module(c)
c.write('EE-114-01-2-short.svg', c.circuit('short'))
