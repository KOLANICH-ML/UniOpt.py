import typing
from os.path import sep as pathSep

import numpy as np
from lazily import evostra
from lazy_object_proxy import Proxy

from ..core.ArraySpec import HyperparamArray
from ..core.MetaSpec import *
from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..imports import *
from ..utils import resolveAvailablePath


class EvoStraSpecArrayDict(HyperparamArray):
	@classmethod
	def dict2native(cls, hyperparamsNative: typing.Dict[str, typing.Any], spec) -> typing.Dict[str, typing.Any]:
		spaceSpec = np.array(super().dict2native(hyperparamsNative, spec))
		return {"dimension": spaceSpec.shape[0], "var_lower": spaceSpec[:, 1], "var_upper": spaceSpec[:, 2], "var_type": spaceSpec[:, 0]}


class EvoStraSpec(MSpec(isArray=True, scalarMode=ScalarMetaMap.noScalars, integerMode=IntegerMetaMap.noIntegers)):
	hyperparamsSpecType = EvoStraSpecArrayDict

	class HyperparamsSpecsConverters:
		def randint(k, dist, tp):
			return ("I", dist.a, dist.b)

		def uniform(k, dist, tp):
			return (tp.__name__[0].upper(), dist.ppf(0), dist.ppf(1))


class EvoStra(GenericOptimizer):
	specType = RBFOptSpec

	optimizer = None

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, std=0.5, popSize=50, learningRate=0.1) -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)
		self.std = std
		self.popSize = popSize
		self.learningRate = learningRate

	def prepareScoring(self, spaceSpec: typing.Tuple[typing.Tuple[str, float, float], typing.Tuple[str, int, int]]) -> typing.Tuple[int, str, typing.Tuple[typing.Tuple[str, float, float], typing.Tuple[str, int, int]]]:
		return (self.iters, "evostra " + self.__class__.optimizer, spaceSpec)

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, spaceSpec) -> np.ndarray:
		def evostraScore(hyperparams):
			return -fn(hyperparams)[0]

		spaceSpec = np.array(spaceSpec)
		initialPoint = spaceSpec.mean(axis=1)

		es = EvolutionStrategy(initialPoint, evostraScore, population_size=self.popSize, sigma=self.std, learning_rate=self.learningRate, decay=1.0, num_threads=self.jobs)
		res = es.run(self.iters / self.popSize, print_step=None)
		return res
