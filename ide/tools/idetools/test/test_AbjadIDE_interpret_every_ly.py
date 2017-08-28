import ide
abjad_ide = ide.AbjadIDE(is_test=True)


def test_AbjadIDE_interpret_every_ly_01():
    r'''In materials directory.
    '''

    with ide.Test():
        sources = [
            ide.Path('red_score').materials / name / 'illustration.ly'
            for name in ['magic_numbers', 'ranges', 'tempi']
            ]
        targets = [_.with_suffix('.pdf') for _ in sources]
        for target in targets:
            target.remove()

        input_ = 'red~score mm lyi* q'
        abjad_ide._start(input_=input_)
        transcript = abjad_ide._io_manager._transcript.contents
        assert 'Interpreting every ly ...' in transcript
        for source, target in zip(sources, targets):
            assert 'Interpreting ly ...' in transcript
            assert f'Removing {abjad_ide._trim(target)} ...' not in transcript
            assert f'Interpreting {abjad_ide._trim(source)} ...' in transcript
            assert f'Writing {abjad_ide._trim(target)} ...' in transcript
            assert f'Opening {abjad_ide._trim(target)} ...' not in transcript
        assert 'Total time' in transcript
        assert all(_.is_file() for _ in targets)

        input_ = 'red~score mm lyi* q'
        abjad_ide._start(input_=input_)
        transcript = abjad_ide._io_manager._transcript.contents
        assert 'Interpreting every ly ...' in transcript
        for source, target in zip(sources, targets):
            assert 'Interpreting ly ...' in transcript
            assert f'Removing {abjad_ide._trim(target)} ...' in transcript
            assert f'Interpreting {abjad_ide._trim(source)} ...' in transcript
            assert f'Writing {abjad_ide._trim(target)} ...' in transcript
            assert f'Opening {abjad_ide._trim(target)} ...' not in transcript
        assert 'Total time' in transcript
        assert all(_.is_file() for _ in targets)


def test_AbjadIDE_interpret_every_ly_02():
    r'''In segments directory.
    '''

    with ide.Test():
        sources = [
            ide.Path('red_score').segments / name / 'illustration.ly'
            for name in ['segment_01', 'segment_02', 'segment_03']
            ]
        targets = [_.with_suffix('.pdf') for _ in sources]
        for target in targets:
            target.remove()

        input_ = 'red~score gg lyi* q'
        abjad_ide._start(input_=input_)
        transcript = abjad_ide._io_manager._transcript.contents
        assert 'Interpreting every ly ...' in transcript
        for source, target in zip(sources, targets):
            assert 'Interpreting ly ...' in transcript
            assert f'Removing {abjad_ide._trim(target)} ...' not in transcript
            assert f'Interpreting {abjad_ide._trim(source)} ...' in transcript
            assert f'Writing {abjad_ide._trim(target)} ...' in transcript
            assert f'Opening {abjad_ide._trim(target)} ...' not in transcript
        assert 'Total time' in transcript
        assert all(_.is_file() for _ in targets)

        input_ = 'red~score gg lyi* q'
        abjad_ide._start(input_=input_)
        transcript = abjad_ide._io_manager._transcript.contents
        assert 'Interpreting every ly ...' in transcript
        for source, target in zip(sources, targets):
            assert 'Interpreting ly ...' in transcript
            assert f'Removing {abjad_ide._trim(target)} ...' in transcript
            assert f'Interpreting {abjad_ide._trim(source)} ...' in transcript
            assert f'Writing {abjad_ide._trim(target)} ...' in transcript
            assert f'Opening {abjad_ide._trim(target)} ...' not in transcript
        assert 'Total time' in transcript
        assert all(_.is_file() for _ in targets)
