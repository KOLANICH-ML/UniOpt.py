import typing
from functools import partial

from lazily import hyperopt
from lazy_object_proxy import Proxy

from ..core.HyperparamVector import HyperparamVector
from ..core.MetaSpec import *
from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..core.Spec import HyperparamDefinition
from ..imports import *


def hyperoptTrialData(mean, variance):
	return {"loss": mean, "loss_variance": variance, "true_loss": mean, "true_loss_variance": variance, "status": hyperopt.STATUS_OK}


def hyperoptScore(fn: typing.Callable, hyperparams: typing.Dict[str, typing.Union[float, int]]) -> typing.Dict[str, typing.Union[NumericT, str]]:
	res = fn(hyperparams)
	return hyperoptTrialData(res[0], res[1])


class distsArgsRemap:
	def randint(dist):
		return [dist.a, dist.b]

	def uniform(dist):
		return [dist.ppf(0), dist.ppf(1)]

	def norm(dist):
		return [dist.mean(), dist.std()]


class distsNamesRemap:
	norm = "normal"


def getNativeHyperoptDist(tp: typing.Union[typing.Type[float], typing.Type[int]], distName: str) -> typing.Callable:

	if hasattr(distsNamesRemap, distName):
		distName = getattr(distsNamesRemap, distName)

	tDistName = distName
	postProcessFunc = None

	if issubclass(tp, int):
		tDistName = "q" + tDistName
		postProcessFunc = round

	nativeHpDist = None
	hp = hyperopt.hp

	if hasattr(hp, tDistName):
		nativeHpDist = getattr(hp, tDistName)
		if issubclass(tp, int):
			postProcessFunc = int

	elif hasattr(hp, distName):
		nativeHpDist = getattr(hp, distName)

	return nativeHpDist, postProcessFunc


class HyperOptSpec(MSpec(scalarMode=ScalarMetaMap.degenerateCategory)):
	HyperparamsSpecsConverters = None

	def __init__(self, *args, **kwargs):
		self.choices = {}
		super().__init__(*args, **kwargs)

	def transformHyperDefItemUniversal(self, k: str, v: typing.Union[typing.Tuple[int], HyperparamDefinition]) -> "hyperopt.pyll.base.Apply":
		if isinstance(v, categoricalTypes):
			self.choices[k] = v
			return hyperopt.hp.choice(k, v)
		else:
			dist = v.distribution
			distName = dist.dist.name

			nativeHpDist, postProcessFunc = getNativeHyperoptDist(v.type, distName)
			if nativeHpDist:
				if hasattr(distsArgsRemap, distName):
					args = getattr(distsArgsRemap, distName)(dist)
				else:
					args = [dist.dist.a, dist.dist.b]
					postProcessFunc = round

				if issubclass(v.type, int):
					args.append(1)  # q argument for integer attrs, without it it raises somewhere in hyperopt

				if postProcessFunc:
					self.postProcessors[k].append((postProcessFunc, float))  # hyperopt returns floats instead of ints

				return nativeHpDist(k, *args)
			else:
				return self.transformHyperDefItemUniversal(k, self.distributionToUniform(k, v))


class HyperOptVectorType_(HyperparamVector):
	"""Do not set to `vectorType`. It is used only when getting categorical results from the fitter and passing them back"""

	@classmethod
	def dict2native(cls, dic: typing.Dict[str, typing.Any], spec) -> typing.Dict[str, typing.Any]:
		for choiceAttrName, choices in spec.choices.items():
			# no need to check if choiceAttrName in dic
			dic[choiceAttrName] = spec.choices[choiceAttrName].index(dic[choiceAttrName])
		return super().dict2native(dic, spec)

	@classmethod
	def native2dict(cls, native: typing.Dict[str, typing.Any], spec) -> typing.Dict[str, typing.Any]:
		for choiceAttrName, choices in spec.choices.items():
			# no need to check if choiceAttrName in native
			native[choiceAttrName] = choices[native[choiceAttrName]]
		return super().native2dict(native, spec)


class Hyperopt(GenericOptimizer):
	specType = HyperOptSpec
	hyperoptAlgo = None

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None) -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)

	def prepareScoring(self, spaceSpec: typing.Dict[str, "hyperopt.pyll.base.Apply"]) -> typing.Tuple[int, str, typing.Dict[str, "hyperopt.pyll.base.Apply"]]:
		return (self.iters, "hyperopt (" + self.__class__.hyperoptAlgo + ")", {"spaceSpec": spaceSpec, "trials": None})

	def injectPoints(self, pointz, bestPointIndex, context, initialize=False):
		trialsData = []
		if context["trials"] is None:
			context["trials"] = hyperopt.Trials()
		pointz = list(pointz)
		from hyperopt.fmin import generate_trial

		for tid, p in zip(context["trials"].new_trial_ids(len(pointz)), pointz):
			t = generate_trial(tid, HyperOptVectorType_.dict2native(p[0], self.spaceSpec))
			t.update({"state": hyperopt.JOB_STATE_DONE, "result": hyperoptTrialData(*p[1])})
			trialsData.append(t)

		context["trials"].insert_trial_docs(trialsData)
		context["trials"].refresh()

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, context: dict) -> typing.Dict[str, typing.Union[float, int]]:
		hyperoptScore1 = partial(hyperoptScore, fn)
		best = hyperopt.fmin(hyperoptScore1, context["spaceSpec"], algo=getattr(hyperopt, self.__class__.hyperoptAlgo).suggest, trials=context["trials"], max_evals=self.iters + (len(context["trials"].trials) if context["trials"] else 0))
		self.details = context["trials"]
		return HyperOptVectorType_.native2dict(best, self.spaceSpec)


class TPE(Hyperopt):
	hyperoptAlgo = "tpe"


class Random(Hyperopt):
	hyperoptAlgo = "rand"
