import tomlkit
from tomlkit import exceptions


def read_config(path):
    try:
        with open(path, "r") as f:
            config = tomlkit.parse(f.read())
    except (FileNotFoundError, exceptions.ParseError):
        return None

    return config


def write_config(path, config):
    with open(path, "w") as f:
        f.write(tomlkit.dumps(config))
