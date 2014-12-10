# -*- encoding: utf-8 -*-
from abjad import *
import ide
abjad_ide = ide.idetools.AbjadIDE(is_test=True)


def test_BuildFileWrangler_pytest_01():
    r'''Works on all build files in library.
    '''

    input_ = 'uu pt q'
    abjad_ide._run(input_=input_)
    transcript_contents = abjad_ide._transcript.contents

    strings = [
        'Running py.test ...',
        'No testable assets found.',
        ]

    for string in strings:
        assert string in transcript_contents


def test_BuildFileWrangler_pytest_02():
    r'''Works on all files in a single build directory.
    '''

    input_ = 'red~example~score u pt q'
    abjad_ide._run(input_=input_)
    transcript_contents = abjad_ide._transcript.contents

    strings = [
        'Running py.test ...',
        'No testable assets found.',
        ]

    for string in strings:
        assert string in transcript_contents