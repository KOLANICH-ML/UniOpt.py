__all__ = ("ProgressReporter", "defaultProgressReporter")
import sys
import typing


class ProgressReporter:
	"""A class to report progress of optimization to a user"""

	def __init__(self, total, title) -> None:
		raise NotImplementedError()

	def reportHyperparams(self, hyperparams) -> None:
		self.print(hyperparams)

	def reportLoss(self, loss) -> None:
		self.print(loss)

	def print(self, *args, **kwargs) -> None:
		print(*args, **kwargs)

	def write(self, *args, **kwargs):
		raise NotImplementedError()

	def flush(self):
		pass

	def __enter__(self) -> typing.Any:
		raise NotImplementedError()

	def __exit__(self, exc_type, exc_value, traceback):
		raise NotImplementedError()


class DumbProgressReporterBase(ProgressReporter):
	"""Setups basic facilities for printing"""

	def __init__(self, total: int, title: str) -> None:
		self.stream = sys.stderr

	def print(self, *args, **kwargs) -> None:
		kwargs["file"] = self.stream
		return print(*args, **kwargs)

	def flush(self):
		return self.stream.flush()

	def write(self, *args, **kwargs) -> None:
		return self.stream.write(*args, **kwargs)

	def __enter__(self):
		return self

	def __exit__(self, exc_type: None, exc_value: None, traceback: None) -> None:
		pass


class DumbProgressReporter(DumbProgressReporterBase):
	"""Just prints the messages"""

	def __init__(self, total: int, title: str) -> None:
		super().__init__(total, title)
		self.i = 0
		self.total = total
		self.title = title

	def reportHyperparams(self, hyperparams: typing.Dict[str, typing.Any]) -> None:
		super().print(self.title, self.i, "/", self.total, hyperparams)

	def reportLoss(self, loss: typing.Tuple[float, float]) -> None:
		super().print(self.title, self.i, "/", self.total, loss)
		self.i += 1


defaultProgressReporter = DumbProgressReporter

try:
	try:
		from tqdm.autonotebook import tqdm as mtqdm
	except BaseException:
		from tqdm import tqdm as mtqdm

	class TQDMProgressReporter(DumbProgressReporterBase):
		"""Uses an awesome tqdm lib to print progress"""

		def __init__(self, total: int, title: str) -> None:
			super().__init__(total, title)
			self.underlyingStream = self.stream
			self.stream = mtqdm(total=total, desc=title, file=self.stream)

		def flush(self):
			return self.underlyingStream.flush()

		def reportLoss(self, loss: typing.Tuple[float, float]) -> None:
			#super().reportLoss(loss)
			self.write(repr(loss))  # problems: print doesn't work well enough, may be a bug in tqdm
			self.stream.update()

		def reportHyperparams(self, hyperparams: typing.Dict[str, typing.Any]):
			return self.write(repr(hyperparams))  # problems: print doesn't work well enough, may be a bug in tqdm

		def __enter__(self):
			self.stream.__enter__()
			return self

		def __exit__(self, exc_type, exc_value, traceback):
			return self.stream.__exit__(exc_type, exc_value, traceback)

	defaultProgressReporter = TQDMProgressReporter
except ImportError:
	pass

if defaultProgressReporter is DumbProgressReporter:
	try:
		from fish import SwimFishProgressSync, fish_types

		class FishProgressReporter(DumbProgressReporterBase):
			"""Uses `fish` lib to show some shit like swimming fishes"""

			def __init__(self, total, title, type="bass"):
				super().__init__(total, title)
				self.i = 0

				class ProgressFish(SwimFishProgressSync, fish_types[type]):
					pass

				self.fish = ProgressFish(total=total, outfile=self.stream)

			def reportLoss(self, loss):
				super().reportLoss(loss)
				self.fish.animate(amount=self.i)
				self.i += 1

		defaultProgressReporter = FishProgressReporter
	except ImportError:
		pass
