class FlagNotRaisedError(Exception):
	"""Exception raised when unit of throughput is unknown

	Attributes:
		data -- unit of the throughput which caused the error
		message -- Explanation of the error
	"""

	def __init__(self, data, message="Unknown unit for throughput"):
		self.data = data
		self.message = message
		super().__init__(self.message)

	def __str__(self):
		return f'{self.data} -> {self.message}'

class UnknownTypeError(Exception):
	"""Exception raised when bit conversion fails

	Attributes:
		data -- bit value parsed from ParsedData
		message -- Explanation of the error
	"""

	def __init__(self, data, message="Unknown type"):
		self.data = data
		self.message = message
		super().__init__(self.message)

	def __str__(self):
		return f'{self.data} -> {self.message}'