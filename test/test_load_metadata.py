import metadata_specifications


def test_load():
    assert metadata_specifications.get_metadata()[0]['datasource']['name'] == 'Qualifiers full-person equivalent (FPE)'
