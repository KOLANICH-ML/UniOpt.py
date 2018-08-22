import typing

try:
	import psutil

	def getCoreCount():
		return psutil.cpu_count()


except BaseException:

	def getCoreCount():
		return os.cpu_count()
