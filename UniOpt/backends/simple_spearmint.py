from lazily import simple_spearmint
from numpy import ndarray

from ..core.MetaSpec import *
from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..imports import *


class SimpleSpearmintSpec(MSpec(scalarMode=ScalarMetaMap.degenerateCategory, integerMode=IntegerMetaMap.noIntegers)):
	class HyperparamsSpecsConverters:
		def randint(k, dist, tp):
			return __class__._categorical(k, range(dist.a, dist.b))

		# uniform=lambda k, dist, tp: {"type": tp.__name__, "min": dist.a, "max": dist.b}
		def uniform(k, dist, tp):
			return {"type": "float", "min": dist.ppf(0), "max": dist.ppf(1)}  # a bug in simple_spearmint: float is used instead of round

		def _categorical(k, categories):
			return {"type": "enum", "options": categories}


class SimpleSpearmint(GenericOptimizer):
	specType = SimpleSpearmintSpec

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, seedIters: int = 5) -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)

		self.seedIters = seedIters

	def prepareScoring(self, spaceSpec):
		solver = simple_spearmint.SimpleSpearmint(spaceSpec)
		return (self.iters, "SimpleSpearmint", solver)

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, solver):
		def spearmintIteration(suggester):
			suggestion = suggester()
			solver.update(suggestion, fn(suggestion)[0])

		pb.print("Bootstrapping...")
		for i in range(self.seedIters):
			spearmintIteration(solver.suggest_random)

		pb.print("Started predicting")
		for i in range(self.iters - self.seedIters):
			spearmintIteration(solver.suggest)

		self.details = solver
		best, _ = solver.get_best_parameters()
		return best
