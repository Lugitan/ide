# -*- encoding: utf-8 -*-
from abjad import *
import ide
abjad_ide = ide.idetools.AbjadIDE(is_test=True)


def test_ScorePackageWrangler_go_to_score_distribution_files_01():
    r'''From scores to distribution depot.
    '''

    input_ = 'dd q'
    abjad_ide._run(input_=input_)
    titles = [
        'Abjad IDE - scores',
        'Abjad IDE - distribution depot',
        ]
    assert abjad_ide._transcript.titles == titles