from pkgutil import iter_modules

# Turn /cogs into a package and set up an easy-access list of all extension names
EXTENSIONS = [module.name for module in iter_modules(__path__)]
