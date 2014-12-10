# -*- encoding: utf-8 -*-
from abjad import *
import ide
abjad_ide = ide.idetools.AbjadIDE(is_test=True)


def test_StylesheetWrangler_go_to_all_distribution_files_01():
    r'''From stylesheets directory to distribution depot.
    '''

    input_ = 'red~example~score y dd q'
    abjad_ide._run(input_=input_)
    titles = [
        'Abjad IDE - scores',
        'Red Example Score (2013)',
        'Red Example Score (2013) - stylesheets directory',
        'Abjad IDE - distribution depot',
        ]
    assert abjad_ide._transcript.titles == titles


def test_StylesheetWrangler_go_to_all_distribution_files_02():
    r'''From stylesheets depot to distribution depot.
    '''

    input_ = 'yy dd q'
    abjad_ide._run(input_=input_)
    titles = [
        'Abjad IDE - scores',
        'Abjad IDE - stylesheets depot',
        'Abjad IDE - distribution depot',
        ]
    assert abjad_ide._transcript.titles == titles