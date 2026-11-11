# Diagnosis

Gates run in order. On EVRAZ, gate 0 is `not_testable` because there is no tonne series. Gate 1 can compare peripheral temperature spread. Gates that need coke certificates, production, or alkali analyses return `not_testable`. The response is a list of gate objects, not a single cause string.

The twin finder ranks hours with a large peripheral range against hours with a small range, using blast flow as the match variable. It does not claim a production effect.
