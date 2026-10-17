import importlib.util, pathlib
_p = pathlib.Path(__file__).with_name('EE-112-01-3_common.py')
_s = importlib.util.spec_from_file_location('c', _p); c = importlib.util.module_from_spec(_s); _s.loader.exec_module(c)
c.write('EE-112-01-3-short.svg', c.circuit('short'))
