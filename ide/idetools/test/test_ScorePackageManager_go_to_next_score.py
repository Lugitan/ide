# -*- encoding: utf-8 -*-
from abjad import *
import ide
abjad_ide = ide.idetools.AbjadIDE(is_test=True)


def test_ScorePackageManager_go_to_next_score_01():

    input_ = 'red~example~score >> q'
    abjad_ide._run(input_=input_)
    titles = [
        'Abjad IDE - scores',
        'Red Example Score (2013)',
        'Blue Example Score (2013)',
        ]
    assert abjad_ide._transcript.titles == titles