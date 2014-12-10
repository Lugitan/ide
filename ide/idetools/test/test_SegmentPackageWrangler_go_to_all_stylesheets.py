# -*- encoding: utf-8 -*-
from abjad import *
import ide
abjad_ide = ide.idetools.AbjadIDE(is_test=True)


def test_SegmentPackageWrangler_go_to_all_stylesheets_01():
    r'''From segments directory to stylesheets depot.
    '''

    input_ = 'red~example~score g yy q'
    abjad_ide._run(input_=input_)
    titles = [
        'Abjad IDE - scores',
        'Red Example Score (2013)',
        'Red Example Score (2013) - segments directory',
        'Abjad IDE - stylesheets depot',
        ]
    assert abjad_ide._transcript.titles == titles


def test_SegmentPackageWrangler_go_to_all_stylesheets_02():
    r'''From segments depot to stylesheets depot.
    '''

    input_ = 'gg yy q'
    abjad_ide._run(input_=input_)
    titles = [
        'Abjad IDE - scores',
        'Abjad IDE - segments depot',
        'Abjad IDE - stylesheets depot',
        ]
    assert abjad_ide._transcript.titles == titles