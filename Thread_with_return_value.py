from threading import Thread

class ThreadWithReturnValue(Thread):
	
	def __init__(self, group=None, target=None, name=None,
				 args=(), kwargs={}, Verbose=None):
		super().__init__(group, target, name, args, kwargs)
		self._return = None
		self._exception = ''

	def run(self):
		try:
			if self._target is not None:
				self._return = self._target(*self._args, **self._kwargs)
		except Exception as e:
			self._exception = e
	def join(self, *args):
		super().join(*args)
		if self._exception:
			raise self._exception
		return self._return