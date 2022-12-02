from dataquery_processor import QueryBuilder, OdbcQueryRunner, StorageController
from conftest import get_test_file_path


def test_create_and_run_simple_query():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Ethnicity (basic)"},
                {"fieldName": "Sex"}
            ],
        "years": [
                "2020/21"
            ]
    }
    qb = QueryBuilder(manifest)
    q = qb.create_query()
    odbc = OdbcQueryRunner()
    odbc.run_query_and_save_results(q, file_name=get_test_file_path("test_query_runner.csv"))


def test_create_and_run_simple_query_2():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Sex"}
            ],
        "years": [
                "2019/20", "2020/21"
            ]
    }
    qb = QueryBuilder(manifest)
    q = qb.create_query()
    odbc = OdbcQueryRunner()
    odbc.run_query_and_save_results(q, file_name=get_test_file_path("test_query_runner.csv"))


def test_create_and_run_query_with_constraints():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Sex"},
                {"fieldName": "Sex", "allowedValues": ["Female"]}
            ],
        "years": [
            "2019/20", "2020/21"
        ]
    }
    qb = QueryBuilder(manifest)
    q = qb.create_query()
    odbc = OdbcQueryRunner()
    odbc.run_query_and_save_results(q, file_name=get_test_file_path("test_query_runner.csv"))


def test_create_and_run_query_with_multiple_constraints():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Sex"},
                {"fieldName": "Domicile (basic)"},
                {"fieldName": "Sex", "allowedValues": ["Female"]},
                {"fieldName": "Domicile (basic)", "allowedValues": ["UK", "European Union"]}
            ],
        "years": [
            "2020/21"
        ]
    }
    qb = QueryBuilder(manifest)
    q = qb.create_query()
    odbc = OdbcQueryRunner()
    odbc.run_query_and_save_results(q, file_name=get_test_file_path("test_query_runner.csv"))
