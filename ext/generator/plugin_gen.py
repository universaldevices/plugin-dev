
import json
import jsonschema
from jsonschema import validate

#validate a json file based on plugin.schema.json
class JSONSchemaParser:
    def __init__(self, schema_file="./plugin.schema.json"):
        with open(schema_file, 'r') as file:
            self.schema = json.load(file)

    def parse(self, json_file):
        with open(json_file, 'r') as file:
            data = json.load(file)
            try:
                validate(instance=data, schema=self.schema)
                return data
            except jsonschema.exceptions.ValidationError as err:
                print(f"Validation error: {err}")
                return None


class 