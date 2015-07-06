# -*- encoding: utf-8 -*-
from abjad import *
import os
import pytest
import ide
abjad_ide = ide.idetools.AbjadIDE(is_test=True)


def test_SegmentPackageWrangler_interpret_every_illustration_ly_01():
    r'''Does not display candidate messages.
    '''

    with systemtools.FilesystemState(keep=paths):
        for path in pdf_paths:
            os.remove(path)
        assert not any(os.path.exists(_) for _ in pdf_paths)
        input_ = 'red~example~score g ii* y q'
        abjad_ide._run(input_=input_)
        assert all(os.path.isfile(_) for _ in pdf_paths)
        assert systemtools.TestManager._compare_backup(pdf_paths)

    contents = abjad_ide._transcript.contents
    for path in paths:
        assert path in contents

    assert 'Will interpret ...' in contents
    assert 'INPUT:' in contents
    assert 'OUTPUT:' in contents
    assert not 'The files ...' in contents
    assert not '... compare the same.' in contents
    assert not 'Preserved' in contents


@pytest.mark.skipif(
    os.environ.get('TRAVIS') == 'true',
    reason='Cannot build on Travis-CI',
    )
def test_SegmentPackageWrangler_interpret_every_illustration_ly_02():
    r'''Does display candidate messages.
    '''

    with systemtools.FilesystemState(keep=paths):
        input_ = 'red~example~score g ii* y q'
        abjad_ide._run(input_=input_)

    contents = abjad_ide._transcript.contents
    for path in paths:
        assert path in contents

    assert 'Will interpret ...' in contents
    assert 'INPUT:' in contents
    assert 'OUTPUT:' in contents
    assert 'The files ...' in contents
    assert '... compare the same.' in contents
    assert 'Preserved' in contents