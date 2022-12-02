import pytest

from lambda_function import lambda_handler
import json


def test_call_lambda_event():
    manifest = {
        "client": "demo",
        "orderRef": "lambda test",
        "customerRef": "",
        "datasource": "Student full-person equivalent (FPE)",
        "onwardUseCategory": "1",
        "measure": "FPE",
        "items":
            [
                {
                    "fieldName": "Sex",
                    "allowedValues": ["Female"]
                },
                {
                    "fieldName": "Ethnicity (basic)"
                }
            ],
        "years": [
            "2020/21"
        ]
    }
    event = json.dumps({"responsePayload": {"order": manifest}})
    records = {'Records': [{"body": event}]}

    # Check everything works up until the point we try to delete the message from the queue,
    # as our test event doesn't come from a queue.
    with pytest.raises(ValueError, match='No receipt handle for message - cannot delete'):
        lambda_handler(records, None)
