class NoConnectionError(Exception):
	def __init__(self, data, message):
		self.data = data
		self.message = message
		super().__init__(self.message)

	def __str__(self):
		return f'{self.data} -> {self.message}'
