import ide
abjad_ide = ide.AbjadIDE(is_test=True)


def test_AbjadIDE_interpret_preface_01():

    with ide.Test():
        source = ide.Path('red_score').build / 'letter' / 'preface.tex'
        target = source.with_suffix('.pdf')
        target.remove()

        input_ = 'red~score %letter pi q'
        abjad_ide._start(input_=input_)
        transcript = abjad_ide._io_manager._transcript.contents
        assert 'Interpreting preface ...' in transcript
        assert f'Removing {abjad_ide._trim(target)} ...' not in transcript
        assert f'Interpreting {abjad_ide._trim(source)} ...' in transcript
        assert f'Writing {abjad_ide._trim(target)} ...' in transcript
        assert f'Opening {abjad_ide._trim(target)} ...' in transcript
        assert target.is_file()

        input_ = 'red~score %letter pi q'
        abjad_ide._start(input_=input_)
        transcript = abjad_ide._io_manager._transcript.contents
        assert 'Interpreting preface ...' in transcript
        assert f'Removing {abjad_ide._trim(target)} ...' in transcript
        assert f'Interpreting {abjad_ide._trim(source)} ...' in transcript
        assert f'Writing {abjad_ide._trim(target)} ...' in transcript
        assert f'Opening {abjad_ide._trim(target)} ...' in transcript
        assert target.is_file()
