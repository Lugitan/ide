import ide
abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_trash_stylesheet_ily_01():

    with ide.Test():
        path = ide.Path('red_score', 'builds', 'letter-score', 'stylesheet.ily')
        assert path.is_file()

        abjad_ide('red %letter yt q')
        transcript = abjad_ide.io.transcript
        assert f'Trashing {path.trim()} ...' in transcript
        assert not path.exists()

        abjad_ide('red %letter yt q')
        transcript = abjad_ide.io.transcript
        assert f'Missing {path.trim()} ...' in transcript