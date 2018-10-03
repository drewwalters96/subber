# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import configparser
import jsonschema
import logging

logger = logging.getLogger(__name__)

schema = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "secret": {
            "type": "string"
        },
        "password": {
            "type": "string"
        },
        "username": {
            "type": "string"
        }
    },
    "required": ["id", "secret", "password", "username"]
}


def get_config(config_file="subber.cfg"):
    try:
        parser = configparser.ConfigParser()
        with open(config_file) as f:
            parser.read_file(f)
        result = dict(parser.items("reddit-api"))
        jsonschema.validate(result, schema)
        return result
    except FileNotFoundError as notfound:
        logger.critical(("Config file not found. Please add a config file %s "
                        "to the project directory."), config_file)
        raise RuntimeError('Subber config file not loaded.')
    except (configparser.NoSectionError,
            configparser.MissingSectionHeaderError) as nosec:
        logger.critical("Missing header: %s", nosec.message)
        raise RuntimeError('Subber config file not loaded.')
    except jsonschema.exceptions.SchemaError as serr:
        logger.critical("Schema error: %s", serr.message)
        raise RuntimeError('Subber config file not loaded.')
    except jsonschema.exceptions.ValidationError as verr:
        logger.critical("Validation error: %s", verr.message)
        raise RuntimeError('Subber config file not loaded.')


def get_api_config():
    return get_config()
