def load(path: str, module_name: str) -> dict:
    """Load a template from the given path."""
    module = __import__(path)  # , fromlist=[module_name])
    return module.TEMPLATE
