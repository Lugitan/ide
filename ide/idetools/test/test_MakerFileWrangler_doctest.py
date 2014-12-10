# -*- encoding: utf-8 -*-
from abjad import *
import ide
abjad_ide = ide.idetools.AbjadIDE(is_test=True)


def test_MakerFileWrangler_doctest_01():
    r'''In library.
    '''

    input_ = 'kk dt q'
    abjad_ide._run(input_=input_)
    contents = abjad_ide._transcript.contents

    strings = [
        'Running doctest ...',
        'testable assets found ...',
        'tests passed in',
        ]
    for string in strings:
        assert string in contents

    
def test_MakerFileWrangler_doctest_02():
    r'''In score package.
    '''

    input_ = 'red~example~score k dt q'
    abjad_ide._run(input_=input_)
    contents = abjad_ide._transcript.contents

    strings = [
        'Running doctest ...',
        '2 testable assets found ...',
        'RedExampleScoreRhythmMaker.py OK',
        'RedExampleScoreTemplate.py OK',
        '0 of 0 tests passed in 2 modules.',
        ]
    for string in strings:
        assert string in contents