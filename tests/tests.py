#!/usr/bin/env python3
import sys
import unittest
from collections import OrderedDict
from pathlib import Path
from pprint import pprint
from random import randint

import numpy as np
import scipy.stats

thisDir = Path(__file__).parent.absolute()
sys.path.append(str(thisDir.parent))

import UniOpt
from funcs import ackleyRosenbrockWithVariance
from UniOpt.backends.ecabc import BeeColonyGridSpec
from UniOpt.backends.pyshac import PySHACGridSpec
from UniOpt.core.ArraySpec import *
from UniOpt.core.MetaSpec import MSpec
from UniOpt.core.PointsStorage import *
from UniOpt.core.Spec import *
from UniOpt.core.SpecNoIntegers import *
from UniOpt.core.SpecNoScalars import *
from UniOpt.core.SpecOnlyBoxes import ArraySpecOnlyBoxes, ArraySpecOnlyBoxesNoIntegers, SpecOnlyBoxes, SpecOnlyBoxesNoIntegers

specsTestGridSpec = {
	"x": HyperparamDefinition(float, scipy.stats.uniform(loc=0, scale=10)),
	"w": HyperparamDefinition(int, scipy.stats.uniform(loc=0, scale=10)),
	"y": HyperparamDefinition(float, scipy.stats.norm(loc=0, scale=10)),
	"z": 3  # discrete
}


masterInitVec = OrderedDict((
	("x", 0.7),
	("w", 0.7),
	("y", 0.6),
	("z", 3)
))
resultVec = OrderedDict((
	("x", masterInitVec["x"]),
	("w", masterInitVec["w"]),
	("y", specsTestGridSpec["y"].distribution.ppf(masterInitVec["y"])),
	("z", 3)
))

classezToTest = ("DummySpecNoScalarsCategoricalNoIntegers", "DummyArraySpecNoScalarsCategorical", "DummyArraySpecToIntegers", "DummyArraySpecNoScalarsDumbToIntegers", "DummyArraySpecNoScalarsCategoricalToIntegers", "DummyArraySpecNoScalarsCategoricalNoIntegers", "DummyArraySpecNoScalarsDumbNoIntegers", "DummyArraySpecNoScalarsDumb", "DummyArraySpecNoIntegers", "DummyArraySpec", "DummySpec", "DummySpecNoIntegers", "DummySpecNoScalarsCategoricalToIntegers")
classezToTest = [MSpec(clsName) for clsName in classezToTest]
classezToTest.extend((SpecOnlyBoxes, ArraySpecOnlyBoxesNoIntegers, SpecOnlyBoxesNoIntegers, ArraySpecOnlyBoxes))


class TestSpecsClasses(unittest.TestCase):
	def assertIsSubclass(self, cls, superCls, msg=None):
		if not issubclass(cls, superCls):
			self.fail(self._formatMessage(msg, repr(cls) + " is not a subclass of " + repr(superCls)))

	def assertForBasicClass(self, cls, basicCls):
		if issubclass(cls, basicCls):
			self.assertIsSubclass(cls.hyperparamsVectorType, basicCls.hyperparamsVectorType)
			self.assertIsSubclass(cls.hyperparamsSpecType, basicCls.hyperparamsSpecType)

	def assertions4ASpecClass(self, cls):
		basicClasses = (
			SpecNoIntegers,
			SpecToIntegers,
			SpecNoScalarsDumb,
			SpecNoScalarsCategorical,
			ArraySpec
		)
		for basicCls in basicClasses:
			self.assertForBasicClass(cls, basicCls)

	def testSpecsClasses(self):
		for cls in classezToTest:
			with self.subTest(specClass=cls):
				#print(cls, [scls.__name__ for scls in cls.mro()])
				#print(cls.hyperparamsVectorType, [scls.__name__ for scls in cls.hyperparamsVectorType.mro()[:-1]])
				#print(cls.hyperparamsSpecType, [scls.__name__ for scls in cls.hyperparamsSpecType.mro()[:-1]])
				self.assertions4ASpecClass(cls)

	def testSpecsInheritedClasses(self):
		for cls in classezToTest:
			with self.subTest(specClass=cls):

				class InheritedClass(cls):
					pass

				self.assertions4ASpecClass(cls)


class TestSpecs(unittest.TestCase):
	def assertionsOnHyperparamsVector(self, cls, b):
		self.assertEqual(b["x"], resultVec["x"])
		self.assertIsInstance(b["x"], float)

		if issubclass(cls, SpecNoIntegers):
			self.assertEqual(b["w"], float2int(resultVec["w"]))
			self.assertIsInstance(b["w"], int)
		elif issubclass(cls, SpecToIntegers):
			self.assertEqual(b["w"], int(resultVec["w"]))
			self.assertIsInstance(b["w"], int)
		else:
			self.assertEqual(b["w"], resultVec["w"])
			self.assertIsInstance(b["w"], float)

		self.assertEqual(b["y"], resultVec["y"])
		self.assertIsInstance(b["y"], float)

		self.assertEqual(b["z"], resultVec["z"])
		self.assertIsInstance(b["z"], int)

	def generateTestHPVec(self, cls):
		hpInitVec = type(masterInitVec)(masterInitVec)
		if issubclass(cls, DummySpec) or hasattr(cls, "HyperparamsSpecsConverters") and hasattr(cls.HyperparamsSpecsConverters, specsTestGridSpec["y"].distribution.dist.name):
			hpInitVec["y"] = resultVec["y"]  # the result is generated by the optimizer itself

		if issubclass(cls, SpecNoScalarsDumb):
			del hpInitVec["z"]
		else:
			# optimizer may transform a categorical int into float !!! DO NOT DELETE!
			if issubclass(cls, SpecToIntegersBase):
				hpInitVec["z"] = float(hpInitVec["z"])  # to test if conversion to int works

		if issubclass(cls.hyperparamsVectorType, HyperparamArray):
			hpInitVec = list(hpInitVec.values())
		else:
			hpInitVec = dict(hpInitVec)
		return hpInitVec

	def genericSpecTest(self, cls):
		hpInitVec = self.generateTestHPVec(cls)

		a = cls(specsTestGridSpec)
		b = a.transformHyperparams(hpInitVec)
		self.assertionsOnHyperparamsVector(cls, b)

		return a, b

	def testGenericSpecs(self):
		for cls in classezToTest:
			with self.subTest(specClass=cls):
				self.genericSpecTest(cls)

	def testBeeColonyGridSpec(self):
		a = BeeColonyGridSpec(specsTestGridSpec)
		b = a.transformHyperparams(self.generateTestHPVec(BeeColonyGridSpec))
		from icecream import ic

		self.assertEqual(b["x"], resultVec["x"])
		self.assertEqual(b["y"], resultVec["y"])
		self.assertEqual(b["z"], resultVec["z"])

		self.assertEqual(a.spec["x"], (0, 10))
		self.assertEqual(a.spec["y"], uniformLimits)
		self.assertEqual(a.spec["w"], (0, 10))

	def testPySHACSpecGridSpec(self):
		import pyshac

		a, b = self.genericSpecTest(PySHACGridSpec)

		self.assertIsInstance(a.spec["x"], pyshac.config.hyperparameters.UniformContinuousHyperParameter)
		self.assertIsInstance(a.spec["y"], pyshac.config.hyperparameters.NormalContinuousHyperParameter)
		self.assertIsInstance(a.spec["w"], pyshac.config.hyperparameters.UniformContinuousHyperParameter)
		self.assertIsInstance(a.spec["z"], pyshac.config.hyperparameters.DiscreteHyperParameter)

		#self.assertionsOnHyperparamsVector()


optimizerTestGridSpec = {
	"x": HyperparamDefinition(float, scipy.stats.uniform(loc=0, scale=10)),
	"y": HyperparamDefinition(int, scipy.stats.norm(loc=0, scale=10)),  # discrete
	# "y": HyperparamDefinition(int, scipy.stats.uniform(loc=0, scale=10)), #discrete
	"z": 3,
}


testStoredPointsToTestInjection = [(p, ackleyRosenbrockWithVariance(p)) for p in ({"x": pp / 5.0, "y": randint(-30, 30) / 3, "z": 3} for pp in range(50))]


def prepareTestStor(cls):
	stor = cls()
	for p, loss in testStoredPointsToTestInjection:
		stor.append(p, loss)
	return stor


class OptimizersTests(unittest.TestCase):
	def assertOnParams(self, params):
		self.assertIsInstance(params["x"], possibleTypesRemap[optimizerTestGridSpec["x"].type])
		self.assertGreaterEqual(params["x"], 0.0)
		self.assertLessEqual(params["x"], 10.0)
		self.assertIsInstance(params["y"], possibleTypesRemap[optimizerTestGridSpec["y"].type])
		self.assertIsInstance(params["z"], possibleTypesRemap[type(optimizerTestGridSpec["z"])])
		self.assertEqual(params["z"], optimizerTestGridSpec["z"])

	def ackleyRosenbrockWithVarianceAndAssert(self, params):
		self.assertOnParams(params)
		return ackleyRosenbrockWithVariance(params)

	#@unittest.skip
	def testOptimizers(self):
		func = self.ackleyRosenbrockWithVarianceAndAssert
		results = {}
		#for optimizer in UniOpt:
		#for optimizer in (UniOpt.BayTuneGP, UniOpt.PySOT, UniOpt.RoBOGP):
		for optimizer in (UniOpt.BeeColony,):
			print("optimizer: " + optimizer.__name__)
			with self.subTest(optimizer=optimizer):
				opt = optimizer(func, optimizerTestGridSpec, iters=100, jobs=1, pointsStorage=prepareTestStor(MemoryStorage))
				res = opt()
				results[optimizer] = (res, func(res))
		results = OrderedDict(((k.__name__, v) for k, v in sorted(results.items(), key=lambda x: x[1][1][0])))
		#if sys.version_info >= (3, 5):
		#	results=dict(results)
		pprint(results)

	@unittest.skip
	def testOptimizer(self):
		func = self.ackleyRosenbrockWithVarianceAndAssert
		opt = UniOpt.GPyOpt(func, optimizerTestGridSpec, iters=100, jobs=1, pointsStorage=prepareTestStor(MemoryStorage))
		res = opt()
		self.assertOnParams(res)


if __name__ == "__main__":
	unittest.main()
