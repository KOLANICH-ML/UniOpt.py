from collections import defaultdict

import numpy as np
import scipy.stats

from ..imports import *
from ..utils import getEffectiveAttrForAClass
from .HyperparamVector import HyperparamVector

eps = scipy.finfo(scipy.float32).eps

possibleTypesRemap = {
	int: (int, np.int16, np.int32, np.int64, np.int_),
	float: (float, np.float16, np.float32, np.float64)
}

IntT = typing.Union.__getitem__(possibleTypesRemap[int])
FloatT = typing.Union.__getitem__(possibleTypesRemap[float])
NumericT = typing.Union[IntT, FloatT]


class HyperparamDefinition:
	"""Used to define a spec. The first argument is data type, the second one is a scipy.stat distribution.
	`randint` means that changing the number has unpredictable effect on the resulting value."""

	__slots__ = ("type", "distribution")

	def __init__(self, type: typing.Union[type, str], distribution):
		self.type = type
		self.distribution = distribution

	def __repr__(self):
		return self.__class__.__name__ + "(" + ", ".join((k + "=" + repr(getattr(self, k)) for k in self.__class__.__slots__)) + ")"


HyperDef = HyperparamDefinition

uniformUnityOffset = 1
#uniformLimits = (uniformUnityOffset * eps, 1.0 - uniformUnityOffset * eps)  # 1 and 0 cannot be used since some distributions have infinity ppf there
uniformLimits = (0.00001, 0.99999)
uniformUnityDistr = HyperDef(float, scipy.stats.uniform(loc=uniformLimits[0], scale=uniformLimits[1] - uniformLimits[0]))

categoricalTypes = (tuple, list)


def float2int(v):
	return int(round(v))


categoricalName = "_categorical"


def getDistrName(hpDef: typing.Any) -> str:
	if isinstance(hpDef, categoricalTypes):
		return categoricalName
	else:
		return hpDef.distribution.dist.name


class SpecProto(object):
	"""Basic spec class. Uses dicts as a spec. Allows to add scalars if optimization is not needed."""

	hyperparamsVectorType = HyperparamVector
	hyperparamsSpecType = HyperparamVector

	class HyperparamsSpecsConverters:
		"""Use it as a mapping distribution name -> function transforming a scipy.stats distribution into optimizer-specific param definition"""

	def transformHyperDefItemUniversal(self, k, v):
		raise NotImplementedError()

	def _transformHyperDefItem(self, k, v):
		"""the internal method is created by metaclass"""
		raise NotImplementedError()

	def __init__(self, genericSpec):
		self.transformHyperDefItemUniversalRecursionLock = False
		self.postProcessors = defaultdict(list)
		spec = self.transformGenericSpec(genericSpec)
		self.spec = spec

	def addAPostProcessorIfNeeded(self, i, k, v):
		pass

	def scalarProcessor(self, i, k, v):
		return v

	def isScalar(self, v):
		return not self.isSpecItem(v)

	def getOptimizerConsumableSpec(self):
		"""Converts the container of a space spec in a semi-processed form (dict but its values are optimizer-specific) into the form optimizer wants."""
		return self.__class__.hyperparamsSpecType.dict2native(self.spec, self)

	def transformGenericSpec(self, genericSpec):
		"""Converts generic spec values into optimizer-specific form"""
		res = {}
		for i, (k, v) in enumerate(genericSpec.items()):
			if self.isScalar(v):
				v = self.scalarProcessor(i, k, v)

			if v is not None:
				if self.isSpecItem(v):
					res[k] = self._transformHyperDefItem(k, v)  # the method is created by metaclass
				else:
					res[k] = v
				self.addAPostProcessorIfNeeded(i, k, v)
		return res

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.spec) + ")"

	def getSpec(self):
		"""Gives spec in its internal form"""
		return self.spec

	def getOptimizerConsumableVector(self, dic: dict):
		"""Converts a dict of points into optimizer-specific format. Useful when wants to inject points into an optimizer."""
		for attrName, postProcessorStack in self.postProcessors.items():
			v = dic[attrName]
			for f in reversed(postProcessorStack):
				v = f[1](v)
				if v is None:
					break
			if v is not None:
				dic[attrName] = v
			else:
				del dic[attrName]
		return self.__class__.hyperparamsVectorType.dict2native(dic, self)

	def transformHyperparams(self, hyperparamsNative):
		"""Used to transform hyperparams returned by a optimizer into black box function consumable form (with respect to its calling convention)"""
		hpVec = self.__class__.hyperparamsVectorType.native2dict(hyperparamsNative, self)
		for attrName, postProcessorStack in self.postProcessors.items():
			if attrName in hpVec:
				v = hpVec[attrName]
			else:
				v = None
			for f in postProcessorStack:
				v = f[0](v)
			hpVec[attrName] = v

		dictForm = dict(hpVec)
		res = self.prepareHyperparamsDict(dictForm)
		return res

	def transformResult(self, hyperparamsNative):
		"""Transforms result in optimizer-specific form into the generic form (just a dict)"""
		return self.transformHyperparams(hyperparamsNative)

	def distributionToUniform_(self, k, hpDef):
		#def printer(v):
		#	print(k, " ", v)
		#	return v
		#self.postProcessors[k].append((printer, printer))
		self.postProcessors[k].append((hpDef.distribution.ppf, hpDef.distribution.cdf))
		if hpDef.type is int:
			self.postProcessors[k].append((float2int, float))
		return uniformUnityDistr

	def distributionToUniform(self, k, hpDef):
		distName = getDistrName(hpDef)
		if distName != "uniform" and distName[0] != "_":
			return self.distributionToUniform_(k, hpDef)
		else:
			return hpDef

	def prepareHyperparamsDict(self, dic: typing.Mapping[str, typing.Any]) -> dict:
		"""Prepares hyperparams dict"""
		return dic

	def isSpecItem(self, item) -> bool:
		"""Returns True if `item` is an item of an abstract generic spec"""
		return isinstance(item, (HyperDef, *categoricalTypes))


def transformHyperDefItemSelect(self, k, v):
	distName = getDistrName(v)

	if hasattr(self.__class__.HyperparamsSpecsConverters, distName):
		if distName[0] == "_":
			return getattr(self.__class__.HyperparamsSpecsConverters, distName)(k, v)
		else:
			return getattr(self.__class__.HyperparamsSpecsConverters, distName)(k, v.distribution, v.type)
	else:
		if self.transformHyperDefItemUniversalRecursionLock:
			raise Exception("Recursion of transformHyperDefItemSelect in " + self.__class__.__name__ + ". " + distName + " is not defined in HyperparamsSpecsConverters.")

		self.transformHyperDefItemUniversalRecursionLock = True
		res = transformHyperDefItemUniversalViaUniform(self, k, v)
		self.transformHyperDefItemUniversalRecursionLock = False
		return res


def transformHyperDefItemUniversalViaUniform(self, k, v):
	return self._transformHyperDefItem(k, self.distributionToUniform(k, v))


class SpecMeta(type):
	"""A metaclass to generate properties for Spec classes. Automatically fills some fields."""

	def __new__(cls, className, parents, attrs, *args, **kwargs):
		isNotARootSpecClass = True
		if isNotARootSpecClass:
			effective = getEffectiveAttrForAClass(("transformHyperDefItemUniversal", "HyperparamsSpecsConverters"), attrs, parents)
			if not effective["transformHyperDefItemUniversal"]:
				attrs["transformHyperDefItemUniversal"] = transformHyperDefItemUniversalViaUniform

			if effective["HyperparamsSpecsConverters"] is not None:
				if hasattr(effective["HyperparamsSpecsConverters"], "uniform"):
					attrs["_transformHyperDefItem"] = transformHyperDefItemSelect
				else:
					raise Exception(repr(effective["HyperparamsSpecsConverters"]) + " contains no `uniform`. Class must either define or inherit a converter for uniform distribution `HyperparamsSpecsConverters.uniform` or an own converter function `transformHyperDefItemUniversal`, or both.")
			else:
				if effective["transformHyperDefItemUniversal"]:
					attrs["_transformHyperDefItem"] = effective["transformHyperDefItemUniversal"]
				else:
					raise Exception("`" + className + ".transformHyperDefItemUniversal` is not defined. Class must either define or inherit a converter for uniform distribution `HyperparamsSpecsConverters.uniform` or an own converter function `transformHyperDefItemUniversal`, or both")
		else:
			metaclassFirstClassInitialized = True

		return super().__new__(cls, className, parents, attrs, *args, **kwargs)


class Spec(SpecProto, metaclass=SpecMeta):
	"""A base class representing optimizer initializing and calling convention."""

	HyperparamsSpecsConverters = None
	transformHyperDefItemUniversal = transformHyperDefItemSelect


class DummySpec(Spec):
	"""A trivial spec, just returns input. Used mainly for testing purposes"""

	def transformHyperDefItemUniversal(self, k, v):
		return v
