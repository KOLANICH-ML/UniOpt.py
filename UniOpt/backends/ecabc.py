import typing
import warnings
from math import sqrt

from lazily.ecabc import abc

from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import HyperparamDefinition
from ..core.SpecOnlyBoxes import SpecOnlyBoxes
from ..imports import *
from ..utils import notInitializedFunction
from ..utils.coresCount import getCoreCount


class BeeColonyGridSpec(SpecOnlyBoxes):
	class HyperparamsSpecsConverters:
		def uniform(k: str, dist, tp: type):
			res = (float(dist.ppf(0)), float(dist.ppf(1)))

			if tp is int:
				res = tuple(int(round(e)) for e in res)

			return res


maxDefaultAmountOfEmployers = 50

from icecream import ic


class BeeColony(GenericOptimizer):
	specType = BeeColonyGridSpec

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 1, pointsStorage: PointsStorage = None, numEmployers=None) -> None:
		if jobs is None:
			self.jobs = getCoreCount()

		if jobs != 1:
			warnings.warn("Multiprocessing is not supported for this solver: it uses `pickle` and you will get AttributeError: Can't pickle local object 'BeeColony.invokeScoring.<locals>.abcScore' . Setting count of jobs to 1")
			jobs = 1

		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)

		if numEmployers is None:
			numEmployers = min(round(sqrt(iters)), maxDefaultAmountOfEmployers)

		self.numEmployers = numEmployers

		self.generations = iters // numEmployers

	def prepareScoring(self, spaceSpec) -> typing.Tuple[int, str, typing.Iterable[typing.List[typing.Union[str, typing.Tuple[float, float], typing.Tuple[int, int]]]]]:
		ic(spaceSpec)
		colony = abc.ABC(self.numEmployers, objective_fn=notInitializedFunction, num_processes=self.jobs)
		for name, limits in spaceSpec.items():
			colony.add_param(min_val=limits[0], max_val=limits[1], name=name)
		
		return (self.iters, "BeeColony", colony)

	def injectPoints(self, pointz, bestPointIndex, colony, initialize=False):
		if initialize:
			for employersInitialized, p in enumerate(pointz):
				if employersInitialized >= colony._num_employers:
					break
				employer = abc.Bee(p[0])
				employer.score = p[1][0]
				colony._employers.append(employer)
			colony._num_employers = colony._num_employers - employersInitialized  # rest of points, will be inserted by create_employers. create_employers creates colony._num_employers employers
		else:
			raise NotImplementedException("Mixing values into partially initialized _employers is not yet implemented")

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, colony) -> typing.List[typing.Union[float, int]]:
		def abcScore(hyperparamsDict):
			return fn(hyperparamsDict)[0]

		colony._fitness_fxn = abcScore
		#colony._minimize = True
		#colony._args # TODO: keyword arguments
		colony.create_employers()  # inserting missing employers. create_employers creates colony._num_employers employers
		colony._num_employers = self.numEmployers
		for i in range(self.generations):
			colony.run_iteration()
		return colony.best_performer[1]
