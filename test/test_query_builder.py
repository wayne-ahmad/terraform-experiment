from dataquery_processor import QueryBuilder


def test_year_starts():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Ethnicity"},
                {"fieldName": "Fruit"}
            ],
        "years": [
                "2020/21"
            ]
    }
    qb = QueryBuilder(manifest)
    assert qb.get_year_starts() == [2020]
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Ethnicity"},
                {"fieldName": "Fruit"}
            ],
        "years": [
                "2019/20", "2020/21"
            ]
    }
    qb = QueryBuilder(manifest)
    assert qb.get_year_starts() == [2019, 2020]


def test_simple_query():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Ethnicity"},
                {"fieldName": "Fruit"}
            ],
        "years": [
                "2020/21"
            ]
    }
    qb = QueryBuilder(manifest)
    q = qb.create_query()
    assert q[0] == 'SELECT "Ethnicity","Fruit",SUM("Unrounded FPE") "Unrounded FPE" FROM "dbo"."fake" WHERE "Onward use category 1"=1 AND "Academic year start" IN (2020) GROUP BY "Ethnicity","Fruit"'


def test_simple_query_with_constraint():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Ethnicity"},
                {"fieldName": "Fruit", "allowedValues": ["banana"]}
            ],
        "years": [
                "2020/21"
            ]
    }
    qb = QueryBuilder(manifest)
    q = qb.create_query()
    assert q[0] == 'SELECT "Ethnicity",SUM("Unrounded FPE") "Unrounded FPE" FROM "dbo"."fake" WHERE "Fruit" IN (?) AND "Onward use category 1"=1 AND "Academic year start" IN (2020) GROUP BY "Ethnicity"'
    assert q[1] == ['banana']


def test_simple_query_with_constraints_2():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Academic year"},
                {"fieldName": "Domicile (UK county/ Non-UK by country/ Unknown)"},
                {"fieldName": "First year marker", "allowedValues": ["First year"]},
                {"fieldName": "First year marker"}
            ],
        "years": [
                "2019/20",
                "2020/21"
            ]
    }
    qb = QueryBuilder(manifest)
    q = qb.create_query()
    assert q[0] == 'SELECT "Academic year","Domicile (UK county/ Non-UK by country/ Unknown)","First year marker",SUM("Unrounded FPE") "Unrounded FPE" FROM "dbo"."fake" WHERE "First year marker" IN (?) AND "Onward use category 1"=1 AND "Academic year start" IN (2019,2020) GROUP BY "Academic year","Domicile (UK county/ Non-UK by country/ Unknown)","First year marker"'
    assert q[1] == ['First year']


def test_simple_query_with_or_constraint():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Ethnicity"},
                {"fieldName": "Fruit", "allowedValues": ["banana", "apple"]}
            ],
        "years": [
                "2020/21"
            ]
    }
    qb = QueryBuilder(manifest)
    q = qb.create_query()
    assert q[0] == 'SELECT "Ethnicity",SUM("Unrounded FPE") "Unrounded FPE" FROM "dbo"."fake" WHERE "Fruit" IN (?,?) AND "Onward use category 1"=1 AND "Academic year start" IN (2020) GROUP BY "Ethnicity"'
    assert q[1] == ['banana', 'apple']


def test_simple_query_with_multiple_or_constraint():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Sex", "allowedValues": ["Female"]},
                {"fieldName": "Fruit", "allowedValues": ["banana", "apple"]}
            ],
        "years": [
                "2020/21"
            ]
    }
    qb = QueryBuilder(manifest)
    q = qb.create_query()
    assert q[0] == 'SELECT SUM("Unrounded FPE") "Unrounded FPE" FROM "dbo"."fake" WHERE "Sex" IN (?) AND "Fruit" IN (?,?) AND "Onward use category 1"=1 AND "Academic year start" IN (2020)'
    assert q[1] == ['Female', 'banana', 'apple']


def test_simple_query_with_text():
    manifest = {
        "datasource": "Student full-person equivalent (fpe)",
        "measure": "FPE",
        "onwardUseCategory": "1",
        "items":
            [
                {"fieldName": "Course title", "allowedValues": ["Stuff"]},
            ],
        "years": [
                "2020/21"
            ]
    }
    qb = QueryBuilder(manifest)
    q = qb.create_query()
    assert q[0] == 'SELECT SUM("Unrounded FPE") "Unrounded FPE" FROM "dbo"."fake" WHERE "Course title" IN (?) AND "Onward use category 1"=1 AND "Academic year start" IN (2020)'
    assert q[1] == ['Stuff']