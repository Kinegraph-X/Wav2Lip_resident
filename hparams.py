

class HParams:
	def __init__(self, **kwargs):
		self.data = {}

		for key, value in kwargs.items():
			self.data[key] = value

	def __getattr__(self, key):
		if key not in self.data:
			raise AttributeError("'HParams' object has no attribute %s" % key)
		return self.data[key]

	def set_hparam(self, key, value):
		self.data[key] = value


# Default hyperparameters
hparams = HParams(

	fps = 25,
	resolution = (480, 270),
	media_folder = "media/",
	ffmpeg_path="ffmpeg/bin/",
	temp_video_file = 'temp/result.mp4',
	local_audio_filename = "recordings/output.wav",
	static_video_file_path="media/Avatar_Small_Master.mp4", # Avatar_Small_Master
	test_video_file="media/lipsynced_avatar.mp4",
	output_video_path = "media/lipsynced_avatar.mp4",
	audio_only_path = 'media/audio_only_lipsynced.wav'
)


def hparams_debug_string():
	values = hparams.values()
	hp = ["  %s: %s" % (name, values[name]) for name in sorted(values) if name != "sentences"]
	return "Hyperparameters:\n" + "\n".join(hp)