import warnings

import numpy as np
from lazy_object_proxy import Proxy

from ..core import LossT
from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..core.SpecOnlyBoxes import ArraySpecOnlyBoxesNoIntegers
from ..imports import *


def createResumableDE():
	from functools import wraps

	from yabox.algorithms.de import DE, DEIterator

	class ResumableDE(DE):
		@wraps(DE.__init__)
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			self._evaluationEnabled = False
			self.initializeIterator()
			self._initialized = False
			self._evaluationEnabled = True

		def initializeIterator(self):
			self._iter = DEIterator(self)  # invokes `init` and `evaluate` hooked by us, returning fake values depending on _evaluationEnabled
			self._initialized = True

		def iterator(self):
			if not self._initialized:
				self.initializeIterator()
			return iter(self._iter)

		def evaluate(self, P):
			if self._evaluationEnabled:
				return super().evaluate(P)
			else:
				return [np.inf] * self.popsize

		def init(self, data=None):
			if self._evaluationEnabled:
				return super().init()
			else:
				return np.array([[np.inf] * self.dims] * self.popsize)

	return ResumableDE


ResumableDE = Proxy(createResumableDE)

# from yabox.algorithms.de import DE, DEIterator


class Yabox(GenericOptimizer):
	specType = ArraySpecOnlyBoxesNoIntegers

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, mutation: typing.Tuple[float, float] = (0.5, 1.0), crossover: float = 0.7, selfAdaptive: bool = False, popSize=None, seed=None) -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)

		self.mutation = mutation
		self.crossover = crossover
		self.selfAdaptive = selfAdaptive
		self.popSize = popSize
		self.seed = seed

	def prepareScoring(self, specSeq: typing.Tuple[typing.Tuple[float, float], typing.Tuple[int, int]]) -> typing.Tuple[int, str, "ResumableDE"]:
		warnings.warn("Multiprocessing is broken for now, https://github.com/pablormier/yabox/issues/33")
		# solver=yabox.PDE(fobj=None, bounds=specSeq, mutation=self.mutation, crossover=self.crossover, maxiters=self.iters, self_adaptive=self.selfAdaptive, popsize=self.popSize, seed=self.seed, processes=self.jobs)

		warnings.warn("Bug with non-returning, see https://github.com/pablormier/yabox/pull/32 for fix")
		solver = ResumableDE(fobj=None, bounds=specSeq, mutation=self.mutation, crossover=self.crossover, maxiters=self.iters, self_adaptive=self.selfAdaptive, popsize=self.popSize, seed=self.seed)
		solver.maxiters //= solver.popsize
		if solver.maxiters < 2:
			solver.maxiters = 2

		return ((solver.maxiters + 1) * solver.popsize, "yabox", solver)

	def injectPoints(self, pointz, bestPointIndex, solver, initialize=False):
		bestPointTranslatedIndex = len(solver._iter.population) + bestPointIndex
		points = []
		losses = []
		for i, p in enumerate(pointz):
			points.append(p[0])
			losses.append(p[1])

		if not solver._initialized:
			newPointsCount = min(solver.popsize, len(points))
			solver._initialized = True
			# assume sorted!
			solver._iter.population[:newPointsCount] = np.array(points[:newPointsCount])
			solver._iter.fitness[:newPointsCount] = losses[:newPointsCount]
			solver._iter.best_idx = bestPointIndex
			solver._iter.best_fitness = losses[bestPointIndex]
		else:
			solver.initializeIterator()

			mergedLosses = np.concatenate((losses, solver._iter.fitness))
			mergedPointsCount = min(solver.popsize, len(mergedLosses))
			order = np.argsort(mergedLosses)[:mergedPointsCount]

			for indexInPop, mergedSortedIndex in enumerate(order):
				if mergedSortedIndex >= solver.popsize:
					hp = solver._iter.population[mergedSortedIndex - mergedPointsCount]
				else:
					hp = points[mergedSortedIndex]
				solver._iter.replacement(indexInPop, hp, losses[mergedSortedIndex])

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, solver: "ResumableDE") -> np.ndarray:
		def yaboxScore(hyperparamsSeq):
			return fn(hyperparamsSeq)

		solver.fobj = yaboxScore
		for iteration in solver.iterator():
			pass

		return iteration.population[iteration.best_idx]
