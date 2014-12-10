# -*- encoding: utf-8 -*-
from abjad import *
import ide
abjad_ide = ide.idetools.AbjadIDE(is_test=True)


def test_MakerFileWrangler_go_home_01():
    r'''From makers directory.
    '''

    input_ = 'red~example~score k hh q'
    abjad_ide._run(input_=input_)
    titles = [
        'Abjad IDE - scores',
        'Red Example Score (2013)',
        'Red Example Score (2013) - makers directory',
        'Abjad IDE - home',
        ]
    assert abjad_ide._transcript.titles == titles


def test_MakerFileWrangler_go_home_02():
    r'''From makers depot.
    '''

    input_ = 'kk hh q'
    abjad_ide._run(input_=input_)
    titles = [
        'Abjad IDE - scores',
        'Abjad IDE - makers depot',
        'Abjad IDE - home',
        ]
    assert abjad_ide._transcript.titles == titles