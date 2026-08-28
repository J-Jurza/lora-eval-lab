You are judging two candidate clinical note sections, A and B, written from the same
doctor-patient conversation. Judge each against the CONVERSATION. The REFERENCE note is
shown only to calibrate the expected format and level of detail; a candidate is not wrong
for differing from the reference if the conversation supports it.

{rubric}

Return JSON only, exactly this shape, scores as integers 1 to 5:
{{"A": {{"faithfulness": 0, "completeness": 0, "format": 0, "concision": 0}},
 "B": {{"faithfulness": 0, "completeness": 0, "format": 0, "concision": 0}},
 "preference": "A" or "B" or "tie",
 "reason": "one sentence"}}

SECTION TO WRITE: {section}

CONVERSATION:
{dialogue}

REFERENCE (calibration only):
{reference}

CANDIDATE A:
{a}

CANDIDATE B:
{b}
