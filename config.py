import tomllib
from pathlib import Path


DATA_PATH = Path() / 'data' / 'config.toml'


with DATA_PATH.open('rb') as fp:
	config = tomllib.load(fp)


def get_config(*parts):
	curr = config
	for part in parts:
		curr = curr[part]
	return curr
