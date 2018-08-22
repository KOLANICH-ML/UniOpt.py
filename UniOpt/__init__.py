import sys

from .backends.bayesian import Bayesian
from .backends.BayTune import BayTuneGCP, BayTuneGCPEi, BayTuneGP, BayTuneGPEi
from .backends.ecabc import BeeColony
from .backends.EvoFuzzy import EvoFuzzy
#from .backends.SMAC import SMAC
from .backends.GPyOpt import GPyOptOptimizer
from .backends.hyperband import HyperBand
from .backends.hyperengine import HyperEngineBayesian, HyperEnginePortfolio
from .backends.hyperopt import TPE, Random
from .backends.optunity import CMA_ES, NelderMead
from .backends.optunity import OptunityOptimizer as Optunity
from .backends.optunity import ParticleSwarm, Sobol
from .backends.pyshac import PySHAC
from .backends.pySOT import PySOT
from .backends.rbfopt import MSRSM, Gutmann
from .backends.RoBO import RoBOForest, RoBOGP
from .backends.simple_spearmint import SimpleSpearmint
from .backends.skopt import SKOptBayesian, SKOptExtraTrees, SKOptForest, SKOptGBTree
from .backends.SOpt import SOptGA, SOptSGA
from .backends.yabox import Yabox
from .backends.ypde import YPDE
from .utils import IterableModule


class Optimizers(IterableModule):
	__all__ = ("TPE", "Random", "Optunity", "ParticleSwarm", "Sobol", "NelderMead", "BeeColony", "Yabox", "PySHAC", "HyperEngineBayesian", "HyperEnginePortfolio", "SKOptBayesian", "Forest", "GBTree", "ExtraTrees", "MSRSM", "Gutmann", "HyperBand", "GPyOpt", "Bayesian", "PySOT")
	TPE = TPE
	Random = Random
	Optunity = Optunity
	Bayesian = Bayesian
	BeeColony = BeeColony
	GPyOpt = GPyOptOptimizer
	Yabox = Yabox
	HyperEngineBayesian = HyperEngineBayesian
	HyperEnginePortfolio = HyperEnginePortfolio

	HyperBand = HyperBand

	MSRSM = MSRSM
	Gutmann = Gutmann

	SKOptBayesian = SKOptBayesian
	Forest = SKOptForest
	GBTree = SKOptGBTree
	ExtraTrees = SKOptExtraTrees

	PySHAC = PySHAC

	ParticleSwarm = ParticleSwarm
	Sobol = Sobol
	NelderMead = NelderMead
	CMA_ES = CMA_ES  # seems to be broken in optunity - doesn't catch ConstraintViolation

	#SMAC = SMAC
	Spearmint = SimpleSpearmint  # very slow, broken (predicts the same points) and proprietary

	EvoFuzzy = EvoFuzzy
	YPDE = YPDE

	SOptSGA = SOptSGA
	SOptGA = SOptGA

	PySOT = PySOT

	BayTuneGP = BayTuneGP

	RoBOForest = RoBOForest
	RoBOGP = RoBOGP


sys.modules[__name__] = Optimizers(__name__)
