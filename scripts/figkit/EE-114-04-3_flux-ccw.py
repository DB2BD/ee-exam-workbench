import pathlib, importlib.util
spec = importlib.util.spec_from_file_location("c", pathlib.Path(__file__).parent / "EE-114-04-3_common.py"); c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
c.flux_plane([("t", "原接線：合成磁通 "), ("v", "ϕ"), ("n", " = "), ("v", "ϕ"), ("vsub", "m"), ("n", "∠"), ("v", "ϑ")], (45, 135, 225, 315), True, "EE-114-04-3-flux-ccw.svg")
