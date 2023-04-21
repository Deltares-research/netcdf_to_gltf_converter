def test_xugrid_installed_correctly():
    from xugrid import UgridDataArray as arr

    assert arr.grid != None
