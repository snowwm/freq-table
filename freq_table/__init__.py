import pkg_resources

try:
    __version__ = pkg_resources.get_distribution('freq_table').version
except Exception:
    __version__ = 'unknown'
