import warnings

from lazily import diffevo
from numpy import ndarray

from UniOpt.core.ProgressReporter import ProgressReporter
from UniOpt.core.Spec import HyperparamDefinition

from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..core.SpecOnlyBoxes import ArraySpecOnlyBoxesNoIntegers
from ..imports import *


class EvoFuzzy(GenericOptimizer):
	specType = ArraySpecOnlyBoxesNoIntegers

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Dict[str, typing.Union[HyperparamDefinition, int]], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, popSize: int = 30, mutation: float = 0.8, crossover: float = 0.7, mode: str = "best/1") -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)
		assert popSize < iters
		self.popSize = popSize
		self.mode = mode
		self.crossover = crossover
		self.mutation = mutation

	def prepareScoring(self, specSeq: typing.List[typing.Tuple[NumericT, NumericT]]) -> typing.Tuple[int, str, typing.List[typing.Tuple[NumericT, NumericT]]]:
		return (self.iters, "EvoFuzzy diffevo", specSeq)

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, specSeq: typing.Iterable[typing.Tuple[NumericT, NumericT]]) -> ndarray:
		def evofuzzyScore(hyperparamsSeq):
			return fn(hyperparamsSeq)[0]

		for best, unfitness in diffevo.differential_evolution(evofuzzyScore, specSeq, mut=self.mutation, crossprob=self.crossover, popsize=self.popSize, gens=self.iters // self.popSize, mode=self.mode):
			pass
		self.details = unfitness
		return best
