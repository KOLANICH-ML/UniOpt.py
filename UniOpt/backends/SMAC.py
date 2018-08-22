import lazily.smac.optimizer.acquisition as acqTypes
from lazily.smac.facade.smac_facade import SMAC as SMACFacade
from lazily.smac.scenario.scenario import Scenario
from lazily.smac.tae.execute_func import ExecuteTAFuncDict

from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..imports import *
from .ConfigSpaceSpec import ConfigSpaceSpec


class SMAC(GenericOptimizer):
	specType = ConfigSpaceSpec

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, acquisitionType="EI", acquisitionOptimizerType="InterleavedLocalAndRandomSearch", intensifier=None, SMBOClass: "smac.optimizer.smbo.SMBO" = None, acquisitionTradeoff: float = 0.1):
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)
		if isinstance(acquisitionType, str):
			acquisitionType = getattr(acqTypes, acquisitionType)
		self.acquisitionType = acquisitionType

		if isinstance(acquisitionOptimizerType, str):
			import importlib

			optModName = "smac.optimizer." + acquisitionType.__name__.lower() + "_optimization"
			optMod = importlib.import_module(optModName)
			acquisitionOptimizerType = getattr(optMod, acquisitionOptimizerType)
		self.acquisitionOptimizerType = acquisitionOptimizerType
		self.acquisitionTradeoff = acquisitionTradeoff

		self.intensifier = intensifier
		self.SMBOClass = SMBOClass

	def prepareScoring(self, spaceSpec):
		scenario = Scenario({"run_obj": "quality", "cs": spaceSpec, "deterministic": "true", "initial_incumbent": "DEFAULT", "runcount_limit": self.iters})
		modelType = self.createModel()
		acquisition = self.acquisitionType(self.acquisitionTradeoff, model)
		smac = SMACFacade(scenario=scenario, tae_runner=None, acquisition_function=acquisition, acquisition_function_optimizer=self.acquisitionOptimizerType, model=modelType, smbo_class=self.SMBOClass)
		return (self.iters, "SMAC3", smac)

	def createModel(self):
		raise NotImplementedException()

	def invokeScoring(self, fn, pb, smac):
		def smacScore(hyperparamsDict):
			return fn(hyperparamsDict)

		smac.tae_runner = ExecuteTAFuncDict(ta=smacScore)
		best = smac.optimize()
		return best


class SMACRandomForest(SMAC):
	def createModel(self):
		from smac.epm.rf_with_instances import RandomForestWithInstances

		return RandomForestWithInstances()
