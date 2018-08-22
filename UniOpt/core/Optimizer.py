from collections.abc import MutableMapping
from functools import wraps
from warnings import warn

from lazy_object_proxy import Proxy

from ..imports import *
from . import LossT, PointsSequenceT
from .PointsStorage import *
from .ProgressReporter import ProgressReporter, defaultProgressReporter
from .Spec import NumericT, Spec


class PointsInjectionIsNotImplemented(NotImplementedError):
	pass


class Optimizer:
	#blackBoxFunc:int
	#iters:int
	#jobs:int
	#spaceSpec:Dict[str, object]
	#progressReporterClass:typing.type[ProgressReporter]
	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None) -> None:
		self.blackBoxFunc = blackBoxFunc
		self.iters = iters
		self.jobs = jobs
		self.spaceSpec = spaceSpec
		self.progressReporterClass = defaultProgressReporter

		if pointsStorage is None:
			self.pointsStorage = DummyStorage()
		else:
			self.pointsStorage = pointsStorage

	def injectPoints(self, points: PointsSequenceT, bestPointIndex: int, context: object, initialize: bool = False):
		raise PointsInjectionIsNotImplemented()

	def savePoint(self, params: dict, loss: LossT):
		try:
			self.pointsStorage.append(params, loss)
		except Exception as ex:
			warn("Unable to backup point: " + str(ex))

	def prepareCachedPoints(self) -> typing.Tuple[PointsSequenceT, int]:
		"""Prepares cached points: loads them from storage. Returns the points and the best point index"""
		return self.pointsStorage.prepare()

	def resume(self, context):
		"""Injects the state (in the form of saved points) into the used optimizer"""
		try:
			pts, bestIndex = self.prepareCachedPoints()
			if pts and bestIndex is not None:
				self.injectPoints(pts, bestIndex, context, True)
		except PointsInjectionIsNotImplemented:
			warn("Cannot resume: `" + str(self.__class__.__name__) + "` does not have `injectPoint` implemented")

	def __call__(self):
		raise NotImplementedError()


class GenericOptimizer(Optimizer):
	specType = Spec

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None) -> None:
		self.details = None

		spaceSpec = self.__class__.specType(spaceSpec)
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)

	def __call__(self, textMessage: str = "") -> typing.Dict[str, NumericT]:
		"""Does the optimization"""
		total, desc, context = self.prepareScoring(self.spaceSpec.getOptimizerConsumableSpec())

		pr = self.progressReporterClass(total=total, title=desc + " " + textMessage + " ...")

		with self.pointsStorage:
			self.resume(context)
			with pr as pb:
				blackBoxIteration = self.__class__.wrapIteration(self, self.spaceSpec.transformHyperparams, pb)(self.blackBoxFunc)
				best = self.invokeScoring(blackBoxIteration, pb, context)

		best = self.spaceSpec.transformResult(best)

		#hyperparamsTypeCoerce(best)
		assert best is not None
		return best

	@classmethod
	def wrapIteration(cls, optimizer: "GenericOptimizer", prepareHyperparams: typing.Callable, pb: ProgressReporter) -> typing.Callable:
		def decorator(blackBoxFunc):
			@wraps(blackBoxFunc)
			def blackBoxFunc1(hyperparams, *args, **kwargs):
				hyperparams = prepareHyperparams(hyperparams)
				pb.reportHyperparams(hyperparams)

				res = blackBoxFunc(hyperparams, *args, **kwargs)

				optimizer.savePoint(hyperparams, res)
				pb.reportLoss(res)
				return res

			return blackBoxFunc1

		return decorator

	def prepareCachedPoints(self):
		pts, bestIndex = super().prepareCachedPoints()
		return map(lambda p: (self.spaceSpec.getOptimizerConsumableVector(p[0]), p[1]), pts), bestIndex
