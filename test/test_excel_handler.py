from dataquery_processor import ExcelHandler, OdbcQueryRunner, QueryBuilder
from conftest import TEST_OUTPUT_FOLDER
import os

# TODO for these tests also read and check the output


def test_write_excel():
    manifest = {
        "orderRef": "TEST_WRITE_EXCEL",
        "customerRef": "TEST_WRITE_EXCEL",
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Ethnicity (basic)"},
                {"fieldName": "Sex"},
                {"fieldName": "Academic year"}
            ],
        "years": [
                "2020/21"
            ]
    }
    qb = QueryBuilder(manifest)
    q = qb.create_query()
    odbc = OdbcQueryRunner()
    cursor = odbc.run_query_and_return_results(q)
    columns = odbc.get_headers()
    excel_handler = ExcelHandler(manifest=manifest, output_file=TEST_OUTPUT_FOLDER + os.sep + 'excel_test.xlsx')
    excel_handler.__populate_worksheet_from_odbc_cursor__(cursor=cursor, headers=columns)


def test_write_excel_2():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "orderRef": "TEST_WRITE_EXCEL_2",
        "customerRef": "TEST_WRITE_EXCEL_2",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Ethnicity (basic)"},
                {"fieldName": "Sex"},
                {"fieldName": "Academic year"},
                {"fieldName": "Mode of study"}
            ],
        "years": [
                "2020/21"
            ]
    }
    qb = QueryBuilder(manifest)
    q = qb.create_query()
    odbc = OdbcQueryRunner()
    cursor = odbc.run_query_and_return_results(q)
    columns = odbc.get_headers()
    excel_handler = ExcelHandler(manifest=manifest, output_file=TEST_OUTPUT_FOLDER + os.sep + 'excel_test.xlsx')
    excel_handler.__populate_worksheet_from_odbc_cursor__(cursor=cursor, headers=columns)


def test_write_excel_from_file():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "orderRef": "TEST_WRITE_EXCEL_FROM_FILE",
        "customerRef": "TEST_WRITE_EXCEL_FROM_FILE",
        "measure": "Unrounded FPE",
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
    file = 'test' + os.sep + 'test_data.csv'
    excel_handler = ExcelHandler(manifest=manifest, csv_file=file, output_file=TEST_OUTPUT_FOLDER + os.sep + 'excel_test_from_csv.xlsx')
    excel_handler.create_workbook()


def test_write_excel_from_file_no_pivot():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "orderRef": "TEST_WRITE_EXCEL_FROM_FILE_NO_PIVOT",
        "customerRef": "TEST_WRITE_EXCEL_FROM_FILE_NO_PIVOT",
        "measure": "Unrounded FPE",
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
    file = 'test' + os.sep + 'test_data.csv'
    excel_handler = ExcelHandler(manifest=manifest, csv_file=file, output_file=TEST_OUTPUT_FOLDER + os.sep + 'excel_test_from_csv_no_pivot.xlsx')
    excel_handler.create_notes_only()
