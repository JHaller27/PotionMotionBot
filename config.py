import tomllib
from pathlib import Path


DATA_PATH = Path() / 'data' / 'config.toml'


def load_config():
	global config

	with DATA_PATH.open('rb') as fp:
		config = tomllib.load(fp)


def get_config(*parts):
	if config['General']['liveConfigs']:
		load_config()

	curr = config
	for part in parts:
		curr = curr[part]
	return curr


load_config()