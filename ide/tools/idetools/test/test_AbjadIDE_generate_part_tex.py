import ide
abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_generate_part_tex_01():
    
    with ide.Test():
        parts = ide.Path('green_score', 'builds', 'arch-a-parts')
        assert not parts.exists()

        abjad_ide('gre bb parts arch-a-parts arch~a ARCH-A y q')
        path = parts('bass-clarinet-part.tex')
        assert path.is_file()
        
        abjad_ide('gre bb arch-a-parts ag bass q')
        transcript = abjad_ide.io.transcript
        assert f'Writing {path.trim()} ...' in transcript
        assert path.is_file()