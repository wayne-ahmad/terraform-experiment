from dataquery_processor.order_processor import OrderProcessor
import pytest
from dataquery_processor.config import Config
import os


def test_order_no_datasource():
    with pytest.raises(ValueError, match="There is no data source specified"):
        manifest = {
            "orderRef": "test",
            "measure": "FPE",
            "items":
                [
                    {"fieldName": "Ethnicity"},
                    {"fieldName": "Fruit"}
                ],
            "years": [
                    "2020/21"
                ]
        }
        order_processor = OrderProcessor(manifest)
        order_processor.__validate_order__()


def test_order_invalid_datasource():
    with pytest.raises(ValueError, match="The data source in the manifest does not match a metadata specification"):
        manifest = {
            "orderRef": "test",
            "datasource": "Students by FPE",
            "measure": "FPE",
            "items":
                [
                    {"fieldName": "Ethnicity"},
                    {"fieldName": "Fruit"}
                ],
            "years": [
                    "2020/21"
                ]
        }
        order_processor = OrderProcessor(manifest)
        order_processor.__validate_order__()


def test_order_valid_datasource_invalid_field():
    with pytest.raises(ValueError, match="A field in the manifest does not match the metadata specification"):
        manifest = {
            "orderRef": "test",
            "datasource": "Student full-person equivalent (FPE)",
            "measure": "FPE",
            "items":
                [
                    {"fieldName": "Ethnicity"},
                    {"fieldName": "Fruit"}
                ],
            "years": [
                    "2020/21"
                ]
        }
        order_processor = OrderProcessor(manifest)
        order_processor.__validate_order__()


def test_order_valid_datasource():
        manifest = {
            "orderRef": "test",
            "datasource": "Student full-person equivalent (FPE)",
            "measure": "FPE",
            "items":
                [
                    {"fieldName": "Ethnicity (basic)"},
                    {"fieldName": "Sex"}
                ],
            "years": [
                    "2020/21"
                ]
        }
        order_processor = OrderProcessor(manifest)
        order_processor.__validate_order__()


def test_order_valid_datasource_with_warnings():
    manifest = {
        "orderRef": "test",
        "datasource": "Student full-person equivalent (FPE)",
        "measure": "FPE",
        "items":
            [
                {"fieldName": "Ethnicity (basic)"},
                {"fieldName": "Sex"}
            ],
        "years": [
            "2020/21"
        ]
    }
    order_processor = OrderProcessor(manifest)
    order_processor.__validate_order__()
    assert order_processor.notices[0].notice == 'Use of any special category data must be justified'


def test_order_datasource_with_rule_violation():
    with pytest.raises(ValueError, match="The order is invalid as it breaks one or more data rules"):
        manifest = {
            "orderRef": "test",
            "datasource": "Student full-person equivalent (FPE)",
            "measure": "FPE",
            "items":
                [
                    {"fieldName": "Ethnicity (detailed)"},
                    {"fieldName": "Disability (detailed)"}
                ],
            "years": [
                "2020/21"
            ]
        }
        order_processor = OrderProcessor(manifest)
        order_processor.__validate_order__()


def test_order_no_order_ref():
    with pytest.raises(ValueError, match="There is no order reference"):
        manifest = {
            "measure": "FPE",
            "datasource": "Student full-person equivalent (FPE)",
            "items":
                [
                    {"fieldName": "Ethnicity"},
                    {"fieldName": "Fruit"}
                ],
            "years": [
                    "2020/21"
                ]
        }
        order_processor = OrderProcessor(manifest)
        order_processor.__validate_order__()


def test_order_empty_order_ref():
    with pytest.raises(ValueError, match="There is no order reference"):
        manifest = {
            "orderRef": "  ",
            "datasource": "Student full-person equivalent (FPE)",
            "measure": "FPE",
            "items":
                [
                    {"fieldName": "Ethnicity"},
                    {"fieldName": "Fruit"}
                ],
            "years": [
                    "2020/21"
                ]
        }
        order_processor = OrderProcessor(manifest)
        order_processor.__validate_order__()


def test_order_invalid_order_ref():
    with pytest.raises(ValueError, match="The order reference provided is invalid"):
        manifest = {
            "orderRef": "//",
            "datasource": "Student full-person equivalent (FPE)",
            "measure": "FPE",
            "items":
                [
                    {"fieldName": "Ethnicity"},
                    {"fieldName": "Fruit"}
                ],
            "years": [
                    "2020/21"
                ]
        }
        order_processor = OrderProcessor(manifest)
        order_processor.__validate_order__()


def test_order_invalid_constraint():
    with pytest.raises(ValueError, match="Constraint is not in domain of field"):
        manifest = {
            "orderRef": "test",
            "datasource": "Student full-person equivalent (FPE)",
            "measure": "FPE",
            "items":
                [
                    {
                        "fieldName": "Sex",
                        "allowedValues": ["Banana"]
                     },
                ],
            "years": [
                "2020/21"
            ]
        }
        order_processor = OrderProcessor(manifest)
        order_processor.__validate_order__()


def test_order_valid_constraint():
    manifest = {
        "orderRef": "test",
        "datasource": "Student full-person equivalent (FPE)",
        "measure": "FPE",
        "items":
            [
                {
                    "fieldName": "Sex",
                    "allowedValues": ["Female"]
                 },
            ],
        "years": [
            "2020/21"
        ]
    }
    order_processor = OrderProcessor(manifest)
    order_processor.__validate_order__()


def test_order_valid_constraint_no_domain():
    manifest = {
        "orderRef": "test",
        "datasource": "Student full-person equivalent (FPE)",
        "measure": "FPE",
        "items":
            [
                {
                    "fieldName": "Course title",
                    "allowedValues": ["Numerology 101"]
                 },
            ],
        "years": [
            "2020/21"
        ]
    }
    order_processor = OrderProcessor(manifest)
    order_processor.__validate_order__()


def test_order_valid_constraint_no_domain_sanitisied():
    manifest = {
        "orderRef": "test",
        "datasource": "Student full-person equivalent (FPE)",
        "measure": "FPE",
        "items":
            [
                {
                    "fieldName": "Course title",
                    "allowedValues": ["Robert');DROP TABLE student;--"]
                 },
            ],
        "years": [
            "2020/21"
        ]
    }
    order_processor = OrderProcessor(manifest)
    order_processor.__validate_order__()


def test_order_fail_and_rollback():
    # Read a config file with a bad DSN
    config = Config(config_file_name="test"+os.sep+"bad_config.ini")
    manifest = {
        "client": "demo",
        "onwardUseCategory":"3",
        "orderRef": "rollback_test",
        "datasource": "Student full-person equivalent (FPE)",
        "measure": "FPE",
        "items":
            [
                {
                    "fieldName": "Course title",
                    "allowedValues": ["Robert');DROP TABLE student;--"]
                 },
            ],
        "years": [
            "2020/21"
        ]
    }
    with pytest.raises(Exception) as e:
        order_processor = OrderProcessor(manifest, config=config)
        order_processor.process()
    #print(str(e.value))
    path = order_processor.storage_controller.get_output_path()
    assert not os.path.exists(path)


def test_order_replay():
    manifest = {
        "client": "demo",
        "orderRef": "rollback_test_two",
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
    order_processor = OrderProcessor(manifest)
    order_processor.process()
    path = order_processor.storage_controller.get_output_path()
    assert os.path.exists(path)

    # order_processor = OrderProcessor(manifest)
    # order_processor.process()
    # path = order_processor.storage_controller.get_output_path()
    # assert os.path.exists(path)
    #
    # # cleanup
    # shutil.rmtree(path)
    # shutil.rmtree(path)
    # assert not os.path.exists(path)



def test_order_no_items():
    with pytest.raises(ValueError, match="The order contains no items"):
        manifest = {
            "orderRef": "test",
            "datasource": "Student full-person equivalent (FPE)",
            "measure": "FPE",
            "items":
                [],
            "years": [
                "2020/21"
            ]
        }
        order_processor = OrderProcessor(manifest)
        order_processor.__validate_order__()


def test_order_numbers():
    manifest = {
        "orderRef": 123456,
        "customerRef": 2901,
        "datasource": "Student full-person equivalent (FPE)",
        "measure": "FPE",
        "items":
            [
                {"fieldName": "Sex"}
            ],
        "years": [
            "2020/21"
        ]
    }
    order_processor = OrderProcessor(manifest)
    order_processor.__validate_order__()


def test_order_no_results():
    manifest = {
        "client":"demo",
        "customerRef":"",
        "onwardUseCategory": "1",
        "orderRef": "123456",
        "datasource": "Student full-person equivalent (FPE)",
        "measure": "FPE",
        "items":
            [
                {"fieldName": "Sex", "allowedValues": ["Female"]},
                {"fieldName": "HE provider", "allowedValues": ["Hartpury University"]},
                {"fieldName": "HE provider (region)", "allowedValues": ["Wales"]}
            ],
        "years": [
            "2020/21"
        ]
    }
    order_processor = OrderProcessor(manifest)
    order_processor.process()


def test_order_combined():
    manifest = {
        "orderRef": 123456,
        "customerRef": 2901,
        "datasource": "Students and qualifiers full-person equivalent (FPE)",
        "measure": "FPE",
        "items":
            [
                {"fieldName": "Sex"}
            ],
        "years": [
            "2020/21"
        ]
    }
    order_processor = OrderProcessor(manifest)
    order_processor.__validate_order__()