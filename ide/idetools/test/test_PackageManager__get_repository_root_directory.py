# -*- encoding: utf-8 -*-
import os
from abjad import *
import ide
abjad_ide = ide.idetools.AbjadIDE(is_test=True)


def test_PackageManager__get_repository_root_directory_01():

    score_path = os.path.join(
        abjad_ide._configuration.example_score_packages_directory,
        'red_example_score',
        )
    manager = ide.idetools.PackageManager(
        path=score_path,
        session=abjad_ide._session,
        )

    repository_root_directory = manager._get_repository_root_directory()
    score_manager_root_directory = manager._configuration.score_manager_root_directory
    assert repository_root_directory == score_manager_root_directory