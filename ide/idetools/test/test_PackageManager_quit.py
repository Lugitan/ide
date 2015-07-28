# -*- encoding: utf-8 -*-
from abjad import *
import ide
abjad_ide = ide.idetools.AbjadIDE(is_test=True)


def test_PackageManager_quit_01():
    r'''In material package.
    '''
    
    input_ = 'red~example~score m tempo~inventory q'
    abjad_ide._run(input_=input_)
    contents = abjad_ide._transcript.contents

    assert contents


def test_PackageManager_quit_02():
    r'''In segment package.
    '''
    
    input_ = 'red~example~score g A q'
    abjad_ide._run(input_=input_)
    contents = abjad_ide._transcript.contents

    assert contents