# -*- coding: utf-8 -*-
from abjad import *
import ide
abjad_ide = ide.tools.idetools.AbjadIDE(is_test=True)


def test_AbjadIDE_git_status_01():
    r'''Available in all directories except scores directory.
    '''

    input_ = 'st ? q'
    abjad_ide._start(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents
    assert 'git - add (add)' not in contents

    input_ = 'red~example~score st ? q'
    abjad_ide._start(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents
    assert 'git - add (add)' in contents

    input_ = 'red~example~score bb ? q'
    abjad_ide._start(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents
    assert 'git - add (add)' in contents

    input_ = 'red~example~score dd ? q'
    abjad_ide._start(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents
    assert 'git - add (add)' in contents

    input_ = 'red~example~score ee ? q'
    abjad_ide._start(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents
    assert 'git - add (add)' in contents

    input_ = 'red~example~score kk ? q'
    abjad_ide._start(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents
    assert 'git - add (add)' in contents

    input_ = 'red~example~score mm ? q'
    abjad_ide._start(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents
    assert 'git - add (add)' in contents

    input_ = 'red~example~score mm magic~numbers ? q'
    abjad_ide._start(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents
    assert 'git - add (add)' in contents

    input_ = 'red~example~score gg ? q'
    abjad_ide._start(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents
    assert 'git - add (add)' in contents

    input_ = 'red~example~score gg A ? q'
    abjad_ide._start(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents
    assert 'git - add (add)' in contents

    input_ = 'red~example~score yy ? q'
    abjad_ide._start(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents
    assert 'git - add (add)' in contents

    input_ = 'red~example~score tt ? q'
    abjad_ide._start(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents
    assert 'git - add (add)' in contents