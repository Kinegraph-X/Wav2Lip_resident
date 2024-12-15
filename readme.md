### Workers for the Wav2Lip_with_cache

Run the 2 workers on your local machine, and eventually capture the output of the video_playback window via OBS, for a happy anonymous livestream :)

## Installation

```shell
pip install -r requirements.txt
```

## Usage 

In a shell, run :

```shell
python video_playback_vlc.py
```

To use it with the Wav2Lip_with_cache running on your machine, in another shell, run :

```shell
python worker.py
```

If you're using tunnelling (or any distant server), specify the URL of the server/tunnel :
```shell
python worker.py --ngrok_addr "your_ngrok_endpoint.app"
```