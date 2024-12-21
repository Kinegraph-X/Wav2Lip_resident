@echo off

:: Loop through all passed arguments

:parseArgs
    :: asks for the -foo argument and store the value in the variable FOO
    call:getArgWithValue "-ngrok_addr" "ngrok_addr" "%~1" "%~2" && shift && shift && goto :parseArgs

    :: asks for the -foo argument and store the value in the variable FOO
    call:getArgWithValue "-ssh_addr" "ssh_addr" "%~1" "%~2" && shift && shift && goto :parseArgs

goto:eof

:: =====================================================================
:: This function sets a variable from a cli arg with value
:: 1 cli argument name
:: 2 variable name
:: 3 current Argument Name
:: 4 current Argument Value
:getArgWithValue
if "%~3"=="%~1" (
  if "%~4"=="" (
    REM unset the variable if value is not provided
    set "%~2="
    exit /B 1
  )
  set "%~2=%~4"
  exit /B 0
)
exit /B 1
goto:eof



:: =====================================================================
:: This function sets a variable to value "TRUE" from a cli "flag" argument
:: 1 cli argument name
:: 2 variable name
:: 3 current Argument Name
:getArgFlag
if "%~3"=="%~1" (
  set "%~2=TRUE"
  exit /B 0
)
exit /B 1
goto:eof