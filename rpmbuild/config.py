# Python 2/3 Compatibility
try:
    from ConfigParser import ConfigParser
    from StringIO import StringIO
except ImportError:
    from configparser import ConfigParser
    from io import StringIO

from collections import defaultdict
import os


DEFAULT_TIMEOUT = '600'


def read_config(config_file):
    config = ConfigParser()
    config.readfp(StringIO(config_file))

    section = 'docker'
    config_dict = {}
    if config.has_section(section):
        if config.has_option(section, 'version'):
            config_dict.update({'version': config.get(section, 'version')})
        if config.has_option(section, 'timeout'):
            config_dict.update({'timeout': config.getint(section, 'timeout')})
        if config.has_option(section, 'base_url'):
            config_dict.update({'base_url': config.get(section, 'base_url')})

        # Remove None values.
        config_dict = dict((k, v) for k, v in config_dict.items() if v)

    return defaultdict(None, config_dict)


def get_docker_config(docopt_args):
    docker_config = defaultdict(None)
    docker_config_overrides = defaultdict(None)
    docker_config_overrides.update(
        {'base_url': docopt_args['--docker-base_url'],
         'timeout': int(docopt_args['--docker-timeout'] or DEFAULT_TIMEOUT),
         'version': docopt_args['--docker-version']})

    if docopt_args['--config'] is not None and os.path.exists(docopt_args['--config']):
        docker_config = read_config(docopt_args['--config'])

    if docker_config.get('timeout') is None and docker_config_overrides.get('timeout') is None:
        # Since we want to allow --docker-timeout to override config values:
        # we cannot use the default property for docopt to automatically populate
        # docopt_args['--docker-timeout'], hence we insert default value here as
        # mentioned in __doc__ with normal text not being picked up by docopt.
        docker_config_overrides.update({'timeout': int(DEFAULT_TIMEOUT)})

    # Remove None values.
    docker_config_overrides = dict((k, v) for k, v in docker_config_overrides.items() if v)

    # Update docker config with overrides.
    docker_config.update(docker_config_overrides)
    return docker_config
