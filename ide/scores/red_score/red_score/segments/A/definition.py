import abjad


time_signatures = 5 * [(3, 4)]
rh_divisions = []
rh_divisions.extend(4 * [(2, 8)])
rh_divisions.extend(4 * [(2, 16)])
rh_divisions.extend(4 * [(3, 8)])
rh_divisions.extend(4 * [(3, 16)])
lh_divisions = []
lh_divisions.extend(4 * [(3, 8)])
lh_divisions.extend(4 * [(3, 16)])
lh_divisions.extend(4 * [(2, 8)])
lh_divisions.extend(4 * [(2, 16)])
divisions = {
    'RHVoice': rh_divisions,
    'LHVoice': lh_divisions,
    }

maker = abjad.PianoStaffSegmentMaker(
    divisions=divisions,
    include_layout_ly=True,
    time_signatures=time_signatures,
    )
