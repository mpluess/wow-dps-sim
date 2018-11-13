def from_module_import_x(module, x):
    module_loaded = __import__(module, fromlist=[x])
    return getattr(module_loaded, x)
