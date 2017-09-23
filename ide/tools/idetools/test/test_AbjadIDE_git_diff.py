import abjad
import ide
abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_git_diff_01():
    r'''Available everywhere except scores directory.
    '''

    path = ide.Path('red_score')

    abjad_ide('? q')
    transcript = abjad_ide.io.transcript
    assert 'git - diff (diff)' not in transcript

    abjad_ide('red diff q')
    transcript = abjad_ide.io.transcript
    assert f'Git diff {path.contents().trim()} ...' in transcript

    abjad_ide('red bb diff q')
    transcript = abjad_ide.io.transcript
    assert f'Git diff {path.builds().trim()} ...' in transcript

    abjad_ide('red dd diff q')
    transcript = abjad_ide.io.transcript
    assert f'Git diff {path.distribution().trim()} ...' in transcript

    abjad_ide('red ee diff q')
    transcript = abjad_ide.io.transcript
    assert f'Git diff {path.etc().trim()} ...' in transcript

    abjad_ide('red oo diff q')
    transcript = abjad_ide.io.transcript
    assert f'Git diff {path.tools().trim()} ...' in transcript

    abjad_ide('red mm diff q')
    transcript = abjad_ide.io.transcript
    assert f'Git diff {path.materials().trim()} ...' in transcript

    abjad_ide('red %magic diff q')
    transcript = abjad_ide.io.transcript
    assert f"Git diff {path.materials('magic_numbers').trim()} ..." in \
        transcript

    abjad_ide('red gg diff q')
    transcript = abjad_ide.io.transcript
    assert f'Git diff {path.segments().trim()} ...' in transcript

    abjad_ide('red %A diff q')
    transcript = abjad_ide.io.transcript
    assert f"Git diff {path.segments('A').trim()} ..." in transcript

    abjad_ide('red yy diff q')
    transcript = abjad_ide.io.transcript
    assert f'Git diff {path.stylesheets().trim()} ...' in transcript

    abjad_ide('red tt diff q')
    transcript = abjad_ide.io.transcript
    assert f'Git diff {path.test().trim()} ...' in transcript


def test_AbjadIDE_git_diff_02():
    r'''In library directory.
    '''

    if not abjad_ide.test_baca_directories():
        return

    abjad_ide('ll diff q')
    transcript = abjad_ide.io.transcript
    path = ide.Path(abjad.abjad_configuration.composer_library_tools)
    assert f'Git diff {path.trim()} ...' in transcript
