# -*- encoding: utf-8 -*-
from abjad import *
import ide


def test_MaterialPackageWrangler_revert_every_asset_01():

    abjad_ide = ide.idetools.AbjadIDE(is_test=True)
    abjad_ide._session._is_repository_test = True
    input_ = 'red~example~score m rrv* q'
    abjad_ide._run(input_=input_)
    assert abjad_ide._session._attempted_to_revert


def test_MaterialPackageWrangler_revert_every_asset_02():

    abjad_ide = ide.idetools.AbjadIDE(is_test=True)
    abjad_ide._session._is_repository_test = True
    input_ = 'mm rrv* q'
    abjad_ide._run(input_=input_)
    assert abjad_ide._session._attempted_to_revert