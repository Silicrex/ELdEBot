from pkgutil import iter_modules
EXTENSIONS = [module.name for module in iter_modules(__path__)]
