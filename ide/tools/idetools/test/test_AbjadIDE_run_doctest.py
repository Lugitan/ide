import ide
abjad_ide = ide.AbjadIDE(is_test=True)


def test_AbjadIDE_run_doctest_01():
    r'''In score directory.
    '''

    target = ide.Path('red_score')

    input_ = 'red~score dt q'
    abjad_ide._start(input_=input_)
    transcript = abjad_ide._io_manager._transcript.contents
    assert f'Running doctest on {target} ...' in transcript


def test_AbjadIDE_run_doctest_02():
    r'''In tools directory.
    '''

    target = ide.Path('red_score')

    input_ = 'red~score oo dt q'
    abjad_ide._start(input_=input_)
    transcript = abjad_ide._io_manager._transcript.contents
    assert f'Running doctest on {target} ...' in transcript


def test_AbjadIDE_run_doctest_03():
    r'''With caret-navigation to doctest a single file.
    '''

    target = ide.Path('red_score').tools / 'ScoreTemplate.py'

    input_ = 'red~score ^ST q'
    abjad_ide._start(input_=input_)
    transcript = abjad_ide._io_manager._transcript.contents
    assert f'Running doctest on {abjad_ide._trim(target)} ...' in transcript
