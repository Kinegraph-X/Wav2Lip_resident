::@echo off

call retrieve_args.bat -ngrok_addr="%~2" -ssh_addr="%~4"
echo ngrok_addr: %ngrok_addr%
echo ssh_addr: %ssh_addr%

::goto:eof

:: Set window 1: Size and position
START "Lightning_AI_SSH" /D "C:\Production Data\Git\python_projects\Wav2Lip_with_cache" cmd /c "mode con cols=120 lines=16 && title Lightning_AI_SSH && ssh %ssh_addr%"

:: Set window 2: Size and position
START "Video_Playback" /D "C:\Production Data\Git\python_projects\Wav2Lip_resident" cmd /c "mode con cols=120 lines=16 && title Video_Playback && python video_playback_vlc.py"

:: Set window 3: Size and position
START "Local_Worker" /D "C:\Production Data\Git\python_projects\Wav2Lip_resident" cmd /c "mode con cols=120 lines=16 && title Local_Worker && python worker.py --ngrok_addr %ngrok_addr%\"

timeout /t 4

:: Adjust window positions and sizes
nircmd win move ititle "Lightning_AI" 0 10
nircmd win move ititle "Video_Play" -25 273 
nircmd win move ititle "Worker" -50 540
nircmd win move ititle "Mini-E_B_U" 1200 0 