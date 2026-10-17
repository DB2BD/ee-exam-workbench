import pathlib, importlib.util
spec = importlib.util.spec_from_file_location("c", pathlib.Path(__file__).parent / "EE-114-04-3_common.py"); c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
c.flux_plane([("t", "對調 "), ("v", "A"), ("t", "–"), ("v", "A"), ("n", "′"), ("t", "：合成磁通 "), ("v", "ϕ"), ("n", "′ = "), ("v", "ϕ"), ("vsub", "m"), ("n", "∠(−"), ("v", "ϑ"), ("n", ")")], (315, 225, 135, 45), False, "EE-114-04-3-flux-cw.svg")
