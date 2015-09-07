import os

if os.environ.get('DEVENV'):
    import dev_config as config
else:
    import production_config as config
