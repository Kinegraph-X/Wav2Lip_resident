import argparse

parser = argparse.ArgumentParser(description='Worker which records an audio file from the mic, sneds it to a Google Notebook and retrieve the result of the computation')
parser.add_argument('--ngrok_addr', type=str, 
					help='A Ngrok tunnel may have been started from that Public URL',
                    required=False,
                    default='http://127.0.0.1:3000'
                    )
parser.add_argument('--avatar_type', type=str, 
					help='The avater base video that the server shall be using',
                    required=True
                    )
args = parser.parse_args()