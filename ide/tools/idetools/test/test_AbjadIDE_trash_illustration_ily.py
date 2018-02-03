import ide
abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_trash_illustration_ily_01():
    r'''In segment directory.
    '''

    with ide.Test():
        path = ide.Path('red_score', 'segments', 'A', 'illustration.ily')
        path.write_text('')
        assert path.is_file()

        abjad_ide('red %A iit q')
        transcript = abjad_ide.io.transcript
        assert f'Trashing {path.trim()} ...' in transcript
        assert not path.exists()

        abjad_ide('red %A iit q')
        transcript = abjad_ide.io.transcript
        assert f'Missing {path.trim()} ...' in transcript


def test_AbjadIDE_trash_illustration_ily_02():
    r'''In segments directory.
    '''

    with ide.Test():
        paths = []
        for name in ['_', 'A', 'B']:
            path = ide.Path('red_score', 'segments', name, 'illustration.ily')
            path.write_text('')
            assert path.is_file()
            paths.append(path)

        abjad_ide('red gg iit q')
        transcript = abjad_ide.io.transcript
        for path in paths:
            assert f'Trashing {path.trim()} ...' in transcript
            assert not path.exists()

        abjad_ide('red gg iit q')
        transcript = abjad_ide.io.transcript
        for path in paths:
            assert f'Missing {path.trim()} ...' in transcript