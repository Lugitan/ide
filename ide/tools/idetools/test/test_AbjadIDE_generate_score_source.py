import abjad
import filecmp
import ide
import pathlib
abjad_ide = ide.tools.idetools.AbjadIDE(is_test=True)
configuration = ide.tools.idetools.AbjadIDEConfiguration()


def test_AbjadIDE_generate_score_source_01():
    r'''Works when score source already exists.
    '''

    path = pathlib.Path(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'build',
        'letter-portrait',
        'score.tex',
        )

    with abjad.FilesystemState(keep=[path]):
        input_ = 'red~example~score bb letter-portrait sg q'
        abjad_ide._start(input_=input_)
        assert path.is_file()
        assert filecmp.cmp(str(path), str(path) + '.backup')
