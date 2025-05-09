from typing import Any
from worker.app.utils.custom_logs import set_logging

logger = set_logging()

def parse_float(value: Any)->float:
        try:
            result =  float(value) if value is not None else 0.0
            return result
        except (Exception,ValueError,TypeError) as e:
            logger.info("Problem parsing the float value")
            raise Exception(f'Invalid float value: {e}')
    
def parse_int(value:Any)->int:
        try:
            result = int(value) if value is not None else None
            return result
        except Exception as e:
            logger.info("Problem parsing the int value")
            raise Exception(f'invalid int value: {e}')