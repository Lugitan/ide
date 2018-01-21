import ide
abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_trash_preface_tex_01():

    with ide.Test():
        path = ide.Path('red_score', 'builds', 'letter-score', 'preface.tex')
        assert path.is_file()

        abjad_ide('red %letter pt q')
        transcript = abjad_ide.io.transcript
        assert f'Trashing {path.trim()} ...' in transcript
        assert not path.exists()

        abjad_ide('red %letter pt q')
        transcript = abjad_ide.io.transcript
        assert f'No files matching preface.tex ...' in transcript