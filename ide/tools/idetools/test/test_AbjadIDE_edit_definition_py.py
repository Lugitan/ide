# -*- encoding: utf-8 -*-
from abjad import *
import ide


def test_AbjadIDE_edit_definition_py_01():
    r'''In material package.
    '''

    abjad_ide = ide.tools.idetools.Controller(is_test=True)
    input_ = 'red~example~score m magic~numbers de q'
    abjad_ide._run_main_menu(input_=input_)

    assert abjad_ide._session._attempted_to_open_file


def test_AbjadIDE_edit_definition_py_02():
    r'''In segment package.
    '''

    abjad_ide = ide.tools.idetools.Controller(is_test=True)
    input_ = 'red~example~score g A de q'
    abjad_ide._run_main_menu(input_=input_)

    assert abjad_ide._session._attempted_to_open_file