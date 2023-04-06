:: echo.hoon
::
:: These :: symbols are "runes" which denote comments.
::
:: ↓ Print a full stack trace for debugging
!:
::
:: ↓ Declare a function ("gate") with one input, of the type `tape`
|=  word=tape
::
::  ↓ Create `prefix` variable with type `tape`. Assign it a value
=/  prefix=tape  "hoon says: "
::
::  ↓ Concatenate (`weld`) two tapes and assign to `result` variable
=/  result=tape  (weld prefix word)
::
::  ↓ Return the output
result
