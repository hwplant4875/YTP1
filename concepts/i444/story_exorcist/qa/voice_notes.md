# Voice QA, 11/12 KST (Adam, eleven_v4, 58 paragraph takes in voice_orig/)

- check_voice.py: no take missing, longest pause 0.93 s (c1p03), loudness -20.0 to -22.4 LUFS (median -21.5), raw total 27.2 min.
- Its 24 re-voice candidates are whisper mishearings, not voice errors: names (Karras -> Charis, Merrin -> Maren,
  Regan -> Reagan, MacNeil -> McNeil, Bession, Kanavan, Sorenne), homophones (morning/mourning, rites/rights,
  exorcising/exercising) and number formatting ($250,000, 400 million, 1500).
- Every doubtful word was re-heard in isolation (a window of 5 words either side, with a names prompt): all present,
  including "just" (c1p08), "Sarah dies" (c4p08), "Violence" (c5p03), "two hundred and fifty thousand dollars" (c5p06).
  No retake needed.
- Length after the same pause rule as ep08_conjuring/tighten2.py: 25.6 min of narration, so the title number is set
  after the edit (about 26 with the film lines).
