# Workers for the Wav2Lip_with_cache

## Installation

```shell
pip install -r requirements.txt
```

## Usage 

If you're under Windows, ther's a handy batch script to run the workers and ssh into your server (if not already running : needed if you're using an online notebook as a server)

In order to nicelly align the windows, the nircmd (from nirsoft) toolbox needs to be installed on your machine, and the "path" env variable correctly set.

```shell
.\run_avatar_daemon.bat -ngrok_addr="http://your_server_endpoint" -ssh_addr="your server's ssh address"
```

Shutdown all workers by running :

```shell
.\shut_avatar_daemon.bat
```

## In detail

If you need to adapt it to your platform, here's what the script does :

It ssh into your server :

```shell
ssh "your server's ssh address"
```

It runs the 2 workers on your local machine :

```shell
# 1st worker
python video_playback_vlc.py
```

If the Wav2Lip_with_cache server is running on your machine, in another shell, it runs :

```shell
# 2nd worker
python worker.py
```

If you're using tunnelling (or any distant server), it specifies the URL of the server/tunnel :

```shell
# 2nd worker
python worker.py --ngrok_addr "http://your_server_endpoint"
```

## For Livestreamers

Eventually capture the output of the video_playback window via OBS, for a happy anonymous livestream :)