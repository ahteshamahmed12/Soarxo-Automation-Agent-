import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, object] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "agent_id": getattr(record, "agent_id", None),
            "action": getattr(record, "action", None),
            "actor": getattr(record, "actor", None),
            "outcome": getattr(record, "outcome", None),
            "order_id": getattr(record, "order_id", None),
        }
        extra_fields = {
            k: v
            for k, v in record.__dict__.items()
            if k not in logging.LogRecord(
                "", 0, "", 0, "", None, None
            ).__dict__
            and k not in log_entry
        }
        if extra_fields:
            log_entry["metadata"] = extra_fields
        if record.exc_info:
            log_entry["error"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, default=str)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("sorax")
    logger.setLevel(level)
    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    return logger


log = setup_logging()