import math
import typing
from functools import partial

import sklearn
from lazily import hyperband
from numpy import float64

from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..imports import *
from .hyperopt import HyperOptSpec, hyperopt, hyperoptScore
from .sklearn import SKLearnRandomizedSpec

msel = lazyImport("sklearn.model_selection")


class HyperBand(GenericOptimizer):
	specType = SKLearnRandomizedSpec

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None) -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)

	def prepareScoring(self, spaceSpec: typing.Dict[str, typing.Union[scipy.stats._distn_infrastructure.rv_frozen, typing.Tuple[int]]]) -> typing.Tuple[int, str, typing.Dict[str, typing.Union[scipy.stats._distn_infrastructure.rv_frozen, typing.Tuple[int]]]]:
		return (self.iters, "HyperBand", spaceSpec)

	def utilizeNIterations(self, nIterations: IntT, hyperparams: typing.Dict[str, NumericT]) -> None:
		"""Redefine it to make hyperband use nIterations"""
		pass

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, spaceSpec: typing.Dict[str, typing.Union[scipy.stats._distn_infrastructure.rv_frozen, typing.Tuple[int]]]) -> typing.Dict[str, NumericT]:
		s = msel.ParameterSampler(spaceSpec, n_iter=1)

		def sampleParams(s):
			return next(iter(s))

		def hyperbandScore(n_iterations, hyperparams):
			# do something with n_iterations, maybe running an other opt method for n_iterations?
			self.utilizeNIterations(n_iterations, hyperparams)
			return hyperoptScore(fn, hyperparams)

		hb = hyperband.Hyperband(partial(sampleParams, s), hyperbandScore)
		self.trials = hb.run()
		return self.trials[-1]["params"]
