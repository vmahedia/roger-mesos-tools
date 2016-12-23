import sys
import os.path
import yaml
import json

sys.path.insert(0, os.path.abspath('.'))


def fake_config():
    current_dir = os.path.join(os.path.dirname(__file__))
    config_file = os.path.abspath(
        os.path.join(current_dir, 'configs', 'roger-mesos-tools.config')
    )
    with open(config_file, 'r') as f:
        return yaml.load(f.read())


def fake_team_config():
    current_dir = os.path.join(os.path.dirname(__file__))
    config_file = os.path.abspath(
        os.path.join(current_dir, 'configs', 'roger.json')
    )
    with open(config_file, 'r') as f:
        return json.loads(f.read())
