import json
import os
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)

class BookingEventValidator:
    def __init__(self):
        # Load schema from file
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schemas', 'booking_events_schema.json')
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
    
    def validate_message(self, message):
        """
        Validate message against schema
        Returns: (is_valid: bool, error_message: str)
        """
        try:
            validate(instance=message, schema=self.schema)
            return True, None
        except ValidationError as e:
            error_msg = f"Schema validation failed: {e.message}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg