## ENGINEER B - OMALE MOSES

Problem: In reports.py I didn't know if the resolution percentage include the % sign in its return value.

Initial understanding: returning "25.0%" is convenient for printing.

What I verified: the value gets used in the CLI's f"{...}" format string, so returning a string would double the %; also tests can't compare strings to numbers.

Decision: I rejected the string return, kept float, then added a regression test.