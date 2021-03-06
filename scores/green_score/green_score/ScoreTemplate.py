import abjad
import baca
import ide
import green_score


class ScoreTemplate(baca.ScoreTemplate):
    r"""
    Score template.

    >>> import green_score

    ..  container:: example

        >>> green_score.ScoreTemplate()
        ScoreTemplate()

    """

    ### CLASS VARIABLES ###

    _part_manifest = ide.PartManifest(
        ide.Part(section="BassClarinet", section_abbreviation="BCL"),
        ide.Part(section="Violin", section_abbreviation="VN"),
        ide.Part(section="Viola", section_abbreviation="VA"),
        ide.Part(section="Cello", section_abbreviation="VC"),
    )

    ### SPECIAL METHODS ###

    def __call__(self):
        """
        Calls score template.

        Returns score.
        """

        # GLOBAL CONTEXT
        global_context = self._make_global_context()
        # part_names = [_[0] for _ in ScoreTemplate.part_names]
        part_names = [_.name for _ in self.part_manifest.parts]
        tag_string = ".".join(part_names)
        self._attach_lilypond_tag(tag_string, global_context)

        # BASS CLARINET
        bass_clarinet_music_voice = abjad.Voice(
            lilypond_type="BassClarinetMusicVoice",
            name="BassClarinetMusicVoice",
        )
        bass_clarinet_music_staff = abjad.Staff(
            [bass_clarinet_music_voice],
            lilypond_type="BassClarinetMusicStaff",
            name="BassClarinetMusicStaff",
        )
        abjad.annotate(
            bass_clarinet_music_staff,
            "default_instrument",
            green_score.instruments["BassClarinet"],
        )
        abjad.annotate(bass_clarinet_music_staff, "default_clef", abjad.Clef("treble"))
        self._attach_lilypond_tag("BassClarinet", bass_clarinet_music_staff)

        # VIOLIN
        violin_rh_music_voice = abjad.Voice(
            lilypond_type="ViolinRHMusicVoice", name="ViolinRHMusicVoice"
        )
        violin_rh_music_staff = abjad.Staff(
            [violin_rh_music_voice],
            lilypond_type="ViolinRHMusicStaff",
            name="ViolinRHMusicStaff",
        )
        abjad.annotate(violin_rh_music_staff, "REMOVE_ALL_EMPTY_STAVES", True)
        abjad.annotate(violin_rh_music_staff, "default_clef", abjad.Clef("percussion"))
        violin_music_voice = abjad.Voice(
            lilypond_type="ViolinMusicVoice", name="ViolinMusicVoice"
        )
        violin_music_staff = abjad.Staff(
            [violin_music_voice],
            lilypond_type="ViolinMusicStaff",
            name="ViolinMusicStaff",
        )
        abjad.annotate(violin_music_staff, "default_clef", abjad.Clef("treble"))
        violin_staff_group = abjad.StaffGroup(
            [violin_rh_music_staff, violin_music_staff],
            lilypond_type="ViolinStaffGroup",
            name="ViolinStaffGroup",
        )
        abjad.annotate(
            violin_staff_group,
            "default_instrument",
            green_score.instruments["Violin"],
        )
        self._attach_lilypond_tag("Violin", violin_staff_group)

        # VIOLA
        viola_rh_music_voice = abjad.Voice(
            lilypond_type="ViolaRHMusicVoice", name="ViolaRHMusicVoice"
        )
        viola_rh_music_staff = abjad.Staff(
            [viola_rh_music_voice],
            lilypond_type="ViolaRHMusicStaff",
            name="ViolaRHMusicStaff",
        )
        abjad.annotate(viola_rh_music_staff, "REMOVE_ALL_EMPTY_STAVES", True)
        abjad.annotate(viola_rh_music_staff, "default_clef", abjad.Clef("percussion"))
        viola_music_voice = abjad.Voice(
            lilypond_type="ViolaMusicVoice", name="ViolaMusicVoice"
        )
        viola_music_staff = abjad.Staff(
            [viola_music_voice],
            lilypond_type="ViolaMusicStaff",
            name="ViolaMusicStaff",
        )
        abjad.annotate(viola_music_staff, "default_clef", abjad.Clef("alto"))
        viola_staff_group = abjad.StaffGroup(
            [viola_rh_music_staff, viola_music_staff],
            lilypond_type="ViolaStaffGroup",
            name="ViolaStaffGroup",
        )
        abjad.annotate(
            viola_staff_group,
            "default_instrument",
            green_score.instruments["Viola"],
        )
        self._attach_lilypond_tag("Viola", viola_staff_group)

        # CELLO
        cello_rh_music_voice = abjad.Voice(
            lilypond_type="CelloRHMusicVoice", name="CelloRHMusicVoice"
        )
        cello_rh_music_staff = abjad.Staff(
            [cello_rh_music_voice],
            lilypond_type="CelloRHMusicStaff",
            name="CelloRHMusicStaff",
        )
        abjad.annotate(cello_rh_music_staff, "REMOVE_ALL_EMPTY_STAVES", True)
        abjad.annotate(cello_rh_music_staff, "default_clef", abjad.Clef("percussion"))
        cello_music_voice = abjad.Voice(
            lilypond_type="CelloMusicVoice", name="CelloMusicVoice"
        )
        cello_music_staff = abjad.Staff(
            [cello_music_voice],
            lilypond_type="CelloMusicStaff",
            name="CelloMusicStaff",
        )
        cello_staff_group = abjad.StaffGroup(
            [cello_rh_music_staff, cello_music_staff],
            lilypond_type="CelloStaffGroup",
            name="CelloStaffGroup",
        )
        abjad.annotate(
            cello_staff_group,
            "default_instrument",
            green_score.instruments["Cello"],
        )
        abjad.annotate(cello_staff_group, "default_clef", abjad.Clef("bass"))
        self._attach_lilypond_tag("Cello", cello_staff_group)

        # ENSEMBLE STAFF GROUP
        ensemble_staff_group = abjad.StaffGroup(
            [
                bass_clarinet_music_staff,
                violin_staff_group,
                viola_staff_group,
                cello_staff_group,
            ],
            lilypond_type="EnsembleStaffGroup",
            name="EnsembleStaffGroup",
        )

        # MUSIC CONTEXT
        music_context = abjad.Context(
            [ensemble_staff_group],
            lilypond_type="MusicContext",
            name="MusicContext",
        )

        # SCORE
        score = abjad.Score([global_context, music_context], name="Score")
        self._assert_lilypond_identifiers(score)
        self._assert_unique_context_names(score)
        self._assert_matching_custom_context_names(score)
        return score

    ### PUBLIC PROPERTIES ##

    @property
    def known_documents(self):
        """
        Gets known documents.

        ..  container:: example

            >>> score_template = green_score.ScoreTemplate()
            >>> for document_name in score_template.known_documents:
            ...     document_name
            ...
            'ARCH_A_PARTS_BCL'
            'ARCH_A_PARTS_VA'
            'ARCH_A_PARTS_VC'
            'ARCH_A_PARTS_VN'
            'ARCH_A_SCORE'
            'LEDGER_SCORE'

        Returns list of strings.
        """
        known_documents = ["ARCH_A_SCORE", "LEDGER_SCORE"]
        stem = "ARCH_A_PARTS"
        for part in self.part_manifest.parts:
            abbreviation = part.section_abbreviation
            abbreviation = abjad.String(abbreviation).to_shout_case()
            document = f"{stem}_{abbreviation}"
            known_documents.append(document)
        known_documents.sort()
        return known_documents
