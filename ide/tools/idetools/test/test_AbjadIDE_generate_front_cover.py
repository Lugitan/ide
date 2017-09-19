import ide
abjad_ide = ide.AbjadIDE(is_test=True)


def test_AbjadIDE_generate_front_cover_01():

    with ide.Test():
        target = ide.Path('red_score').builds / 'letter' / 'front-cover.tex'
        target.remove()

        abjad_ide('red~score %letter fcg q')
        transcript = abjad_ide.io.transcript
        assert 'Generating front cover ...' in transcript
        assert f'Removing {target.trim()} ...' not in transcript
        assert f'Writing {target.trim()} ...' in transcript
        assert target.is_file()

        abjad_ide('red~score %letter fcg q')
        transcript = abjad_ide.io.transcript
        assert 'Generating front cover ...' in transcript
        assert f'Removing {target.trim()} ...' in transcript
        assert f'Writing {target.trim()} ...' in transcript
        assert target.is_file()