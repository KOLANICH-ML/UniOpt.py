import typing
from os.path import sep as pathSep

import numpy as np
from lazily import rbfopt
from lazy_object_proxy import Proxy

from ..core.ArraySpec import HyperparamArray
from ..core.MetaSpec import *
from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..imports import *
from ..utils import resolveAvailablePath


class RBFOptSpecArrayDict(HyperparamArray):
	@classmethod
	def dict2native(cls, hyperparamsNative: typing.Dict[str, typing.Any], spec) -> typing.Dict[str, typing.Any]:
		spaceSpec = np.array(super().dict2native(hyperparamsNative, spec))
		return {"dimension": spaceSpec.shape[0], "var_lower": spaceSpec[:, 1], "var_upper": spaceSpec[:, 2], "var_type": spaceSpec[:, 0]}


class RBFOptSpec(MSpec(isArray=True, scalarMode=ScalarMetaMap.noScalars, integerMode=IntegerMetaMap.floatIntegers)):
	hyperparamsSpecType = RBFOptSpecArrayDict

	class HyperparamsSpecsConverters:
		def randint(k, dist, tp):
			return ("I", dist.a, dist.b)

		def uniform(k, dist, tp):
			return (tp.__name__[0].upper(), dist.ppf(0), dist.ppf(1))


class RBFOpt(GenericOptimizer):
	specType = RBFOptSpec

	rbfoptAlgo = None

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, maxAlgIterations=None, bonminPath="bonmin", ipoptPath="ipopt", **otherOpts) -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)

		if isinstance(bonminPath, str) and pathSep not in bonminPath:
			bonminPath = resolveAvailablePath(bonminPath)
		if isinstance(ipoptPath, str) and pathSep not in ipoptPath:
			ipoptPath = resolveAvailablePath(ipoptPath)

		if maxAlgIterations is None:
			maxAlgIterations = round(iters * 1.5)

		self.bonminPath = bonminPath
		self.ipoptPath = ipoptPath
		self.maxAlgIterations = maxAlgIterations
		self.otherOpts = otherOpts

	def prepareScoring(self, spaceSpec: typing.Tuple[typing.Tuple[str, float, float], typing.Tuple[str, int, int]]) -> typing.Tuple[int, str, typing.Tuple[typing.Tuple[str, float, float], typing.Tuple[str, int, int]]]:
		return (self.iters, "rbfopt " + self.__class__.rbfoptAlgo, {"spaceSpec": spaceSpec, "x": np.array(()), "y": np.array(())})

	def injectPoints(self, pointz, bestPointIndex, context, initialize=False):
		points = []
		losses = []
		for p in pointz:
			points.append(p[0])
			losses.append(p[1][0])
		points = np.array(points)
		losses = np.array(losses)

		if initialize:
			context["points"] = points
			context["losses"] = losses
		else:
			context["points"] = np.concatenate(points, context["points"])
			context["losses"] = np.concatenate(losses, context["losses"])

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, context: typing.Tuple[typing.Tuple[str, float, float], typing.Tuple[str, int, int]]) -> np.ndarray:
		def rbfoptScore(hyperparams):
			return fn(hyperparams)[0]

		spaceSpec = context["spaceSpec"]
		blackBox = rbfopt.RbfoptUserBlackBox(obj_funct=rbfoptScore, **spaceSpec)
		settings = rbfopt.RbfoptSettings(max_evaluations=self.iters, algorithm=self.__class__.rbfoptAlgo, print_solver_output=False, minlp_solver_path=str(self.bonminPath), nlp_solver_path=str(self.ipoptPath), **self.otherOpts)
		hasPoints = "points" in context and len(context["points"])
		algo = rbfopt.RbfoptAlgorithm(settings, blackBox, init_node_pos=(context["points"] if hasPoints else None), init_node_val=(context["losses"] if hasPoints else None), do_init_strategy=(not hasPoints))

		algo.output_stream = pb

		minCost, best, _, _, _ = algo.optimize()
		self.details = algo
		return best


class Gutmann(RBFOpt):
	rbfoptAlgo = "Gutmann"


class MSRSM(RBFOpt):
	rbfoptAlgo = "MSRSM"
