import warnings

from lazily.sopt.GA.GA import GA
from lazily.sopt.SGA.SGA import SGA

from UniOpt.core.ProgressReporter import ProgressReporter
from UniOpt.core.Spec import HyperDef

from ..core.ArraySpec import HyperparamArray
from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..core.SpecOnlyBoxes import ArraySpecOnlyBoxesNoIntegers
from ..imports import *


class SOptSpecArrayDict(HyperparamArray):
	@classmethod
	def dict2native(cls, hyperparamsNative: typing.Dict[str, typing.Any], spec) -> typing.Dict[str, typing.Any]:
		spaceSpec = np.array(super().dict2native(hyperparamsNative, spec))
		return {"variables_num": spaceSpec.shape[0], "lower_bound": spaceSpec[:, 0], "upper_bound": spaceSpec[:, 1]}


class SOptSpec(ArraySpecOnlyBoxesNoIntegers):
	hyperparamsSpecType = SOptSpecArrayDict

	class HyperparamsSpecsConverters:
		def uniform(k, dist, tp):
			return (dist.ppf(0), dist.ppf(1))


class SOpt(GenericOptimizer):
	specType = SOptSpec
	algoClass = None

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Dict[str, typing.Union[HyperparamDefinition, int]], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, popSize: int = 30, mutation: float = 0.8, crossover: float = 0.7) -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)
		self.popSize = popSize
		self.crossover = crossover
		self.mutation = mutation

	def prepareScoring(self, specSeq: typing.Iterable[scipy.stats._distn_infrastructure.rv_frozen]):
		optimizer = self.__class__.algoClass(func=None, func_type="min", generations=self.iters, cross_rate=self.crossover, mutation_rate=self.mutation, population_size=self.popSize, **specSeq)
		optimizer.generations //= optimizer.population_size
		if optimizer.generations < 2:
			optimizer.generations = 2

		return ((optimizer.generations + 1) * optimizer.population_size, "SOpt", optimizer)

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, optimizer) -> np.ndarray:
		def soptScore(hyperparamsSeq):
			return fn(hyperparamsSeq)[0]

		optimizer.func = soptScore

		res = optimizer.run()
		return optimizer.generations_best_points[optimizer.global_best_index]


class SOptSGA(SOpt):
	algoClass = SGA


class SOptGA(SOpt):
	algoClass = GA
