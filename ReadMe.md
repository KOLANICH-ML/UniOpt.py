UniOpt.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
=========
[![PyPi Status](https://img.shields.io/pypi/v/UniOpt.svg)](https://pypi.org/project/UniOpt)
~~![GitLab Build Status](https://gitlab.com/KOLANICH/UniOpt.py/badges/master/pipeline.svg)~~
~~![GitLab Coverage](https://gitlab.com/KOLANICH/UniOpt.py/badges/master/coverage.svg)~~
~~[![Coveralls Coverage](https://img.shields.io/coveralls/KOLANICH/UniOpt.py.svg)](https://coveralls.io/r/KOLANICH/UniOpt.py)~~
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH/UniOpt.py.svg)](https://libraries.io/github/KOLANICH/UniOpt.py)
[![Code style: antiflash](https://img.shields.io/badge/code%20style-antiflash-FFF.svg)](https://codeberg.org/KOLANICH-tools/antiflash.py)

![Logo](https://gitlab.com/uploads/-/system/project/avatar/8079746/logo1536.jpg?width=40)

This is a universal black box optimization library. No algos (for now) are implemented here, it just implements the framework to wrap as much as possible black box optimizers as easy as possible and to use them in a unified way.

There are differrent hyperparams optimization libs, they use different formats of search space specs, differrent formats of input vectors and differrent ways to retrive the result. This lib smoothes the differences, providing a unified interface to use them all.

This is a **VERY** early alpha. Don't fork for now.

Doxygen documentation [is available](https://kolanich.gitlab.io/UniOpt.py/).

Requirements
------------
* [`numpy`](https://github.com/numpy/numpy) ![Licence](https://img.shields.io/github/license/numpy/numpy.svg) [![PyPi Status](https://img.shields.io/pypi/v/numpy.svg)](https://pypi.org/project/numpy) [![Build status](https://github.com/numpy/numpy/actions/workflows/linux.yml/badge.svg?branch=main)](https://github.com/numpy/numpy/actions/workflows/linux.yml) [![Libraries.io Status](https://img.shields.io/librariesio/github/numpy/numpy.svg)](https://libraries.io/github/numpy/numpy)

* [`scipy`](https://github.com/scipy/scipy) ![Licence](https://img.shields.io/github/license/scipy/scipy.svg) [![PyPi Status](https://img.shields.io/pypi/v/scipy.svg)](https://pypi.org/project/scipy) [![Build status](https://github.com/scipy/scipy/actions/workflows/linux.yml/badge.svg?branch=main)](https://github.com/scipy/scipy/actions/workflows/linux.yml) [![CodeCov Coverage](https://codecov.io/github/scipy/scipy/coverage.svg?branch=master)](https://codecov.io/github/scipy/scipy/) [![Libraries.io Status](https://img.shields.io/librariesio/github/scipy/scipy.svg)](https://libraries.io/github/scipy/scipy)

* [`tqdm`](https://github.com/tqdm/tqdm) ![Licence](https://img.shields.io/github/license/tqdm/tqdm.svg) [![PyPi Status](https://img.shields.io/pypi/v/tqdm.svg)](https://pypi.org/project/tqdm) [![Conda Status](https://anaconda.org/conda-forge/tqdm/badges/version.svg)](https://anaconda.org/conda-forge/tqdm) [![Build Status](https://img.shields.io/github/actions/workflow/status/tqdm/tqdm/test.yml?branch=master&label=tqdm&logo=GitHub)](https://github.com/tqdm/tqdm/actions/workflows/test.yml) [![Coveralls Coverage](https://img.shields.io/coveralls/tqdm/tqdm.svg)](https://coveralls.io/r/tqdm/tqdm) [![CodeCov Coverage](https://codecov.io/github/tqdm/tqdm/coverage.svg?branch=master)](https://codecov.io/github/tqdm/tqdm/) [![Codacy Grade](https://api.codacy.com/project/badge/Grade/3f965571598f44549c7818f29cdcf177)](https://www.codacy.com/app/tqdm/tqdm) [![Libraries.io Status](https://img.shields.io/librariesio/github/tqdm/tqdm.svg)](https://libraries.io/github/tqdm/tqdm)


How to use
----------
0. Select the optimizer backend. Different optimizers are good for different tasks and perform differently. For example, here is the result of optimizing of a test function (a hybrid of Ackley and Rosenbrock functions) as a part of testing:

<details>
<summary>Some benchmarking results</summary>

```python
#20 iters
OrderedDict([
	('MSRSM', ({'x': 3.0754612427874017e-12, 'y': 0}, (1.5205614545266144e-11, 0))),
	('Gutmann', ({'x': 4.495684760769583e-12, 'y': 0}, (2.2224444506946384e-11, 0))),
	('Yabox', ({'x': 0.04484077552690313, 'y': 0}, (0.25594782347174183, 0))),
	('TPE', ({'x': 1.2634392486190837, 'y': 2}, (4.106711553239084, 0))),
	('SKOptForest', ({'x': 2.001450714269141, 'y': 4}, (4.126995218051379, 0))),
	('PySHAC', ({'x': 1.1365327253605517, 'y': 2}, (4.142106739265552, 0))),
	('SKOptGBTree', ({'x': 1.0640782399499173, 'y': 0}, (4.6970480117446005, 0))),
	('Random', ({'x': 2.052104278286049, 'y': 5}, (4.789943923600834, 0))),
	('SKOptBayesian', ({'x': 2.0077415609175713, 'y': 3}, (4.9722440013656195, 0))),
	('GPyOptOptimizer', ({'x': 2.0268674793934447, 'y': 3}, (5.091945147326221, 0))),
	('HyperEnginePortfolio', ({'x': 2.2640333910943444, 'y': 6}, (5.909097060500178, 0))),
	('Bayessian', ({'x': 3.840114588120504, 'y': 13}, (7.910311893451979, 0))),
	('BeeColony', ({'x': 2.1060132176055504, 'y': 0}, (8.303401897709731, 0))),
	('Hyperband', ({'x': 1.0953442448796036, 'y': -7}, (10.21592133952341, 0))),
	('HyperEngineBayessian', ({'x': 0.035178716905066576, 'y': -13}, (11.73027303604122, 0))),
	('NelderMead', ({'x': 5.5546875, 'y': -4}, (16.629806203554303, 0))),
	('ParticleSwarm', ({'x': 9.512831487270224, 'y': -3}, (19.485447083871225, 0))),
	('Sobol', ({'x': 9.621289062499997, 'y': -11}, (19.561767255097276, 0))),
	('OptunityOptimizer', ({'x': 9.57421875, 'y': -13}, (19.665844964264014, 0)))
])

#100 iters
OrderedDict([
	('SKOptBayesian', ({'x': 0.0, 'y': 0}, (0.0, 0))),
	('MSRSM', ({'x': 1.965467987064758e-12, 'y': 0}, (9.71667191151937e-12, 0))),
	('Gutmann', ({'x': 1.994094834174218e-12, 'y': 0}, (9.85878045867139e-12, 0))),
	('Yabox', ({'x': 0.02306337159200547, 'y': 0}, (0.1231750175856301, 0))),
	('HyperEngineBayessian', ({'x': 0.06472343408959413, 'y': 0}, (0.3903313038744054, 0))),
	('Bayessian', ({'x': 0.9829409844977999, 'y': 1}, (2.1634186311845145, 0))),
	('PySHAC', ({'x': 0.2991248121219703, 'y': 0}, (2.383562650155154, 0))),
	('BeeColony', ({'x': 0.7302499236805515, 'y': 1}, (3.9672566629188446, 0))),
	('GPyOptOptimizer', ({'x': 1.9750686145225131, 'y': 4}, (4.101219956972918, 0))),
	('TPE', ({'x': 1.9516353294615343, 'y': 4}, (4.120949851125776, 0))),
	('SKOptGBTree', ({'x': 2.0123977168910847, 'y': 4}, (4.152492764040694, 0))),
	('HyperEnginePortfolio', ({'x': 0.014954151978109342, 'y': 1}, (4.336781434582555, 0))),
	('Random', ({'x': 0.055334114406850876, 'y': 1}, (4.381030185221982, 0))),
	('SKOptForest', ({'x': 2.937967468371783, 'y': 9}, (5.864340107425029, 0))),
	('NelderMead', ({'x': 5.5438690185546875, 'y': -12}, (17.293342096641783, 0))),
	('OptunityOptimizer', ({'x': 9.611312133307793, 'y': -4}, (19.438307138257112, 0))),
	('ParticleSwarm', ({'x': 9.516992187499998, 'y': -3}, (19.48616547955807, 0))),
	('Sobol', ({'x': 9.49560546875, 'y': -9}, (19.607708848977282, 0))),
	('Hyperband', ({'x': 9.454121928413706, 'y': -14}, (19.67098161993487, 0)))
])

#another 100 iters
OrderedDict([
	('SKOptBayesian', ({'x': 0.0, 'y': 0}, (0.0, 0))),
	('MSRSM', ({'x': 1.965467987100698e-12, 'y': 0}, (9.71667191151937e-12, 0))),
	('Gutmann', ({'x': 2.06572139458986e-12, 'y': 0}, (1.021183138050219e-11, 0))),
	('SKOptForest', ({'x': 0.0021370756873140277, 'y': 0}, (0.01064400423985612, 0))),
	('Yabox', ({'x': 0.011806504145005392, 'y': 0},(0.06077385485484399, 0))),
	('Bayessian', ({'x': 0.08963307811319719, 'y': 0}, (0.574643646185228, 0))),
	('SKOptGBTree', ({'x': 1.001876402415787, 'y': 1}, (2.1851226071480934, 0))),
	('TPE', ({'x': 0.9393761906325264, 'y': 1}, (2.273003533796679, 0))),
	('PySHAC', ({'x': 0.3374516167260999, 'y': 0}, (2.68232205052529, 0))),
	('Random', ({'x': 0.5743099848851063, 'y': 0}, (3.91888470632373, 0))),
	('HyperEnginePortfolio', ({'x': 0.020698458554854193, 'y': 1}, (4.340036896917615, 0))),
	('HyperEngineBayessian', ({'x': 0.6695867494591756, 'y': 1}, (4.402848372305214, 0))),
	('GPyOptOptimizer', ({'x': 1.470335759775298, 'y': 2}, (4.5145625430151055, 0))),
	('BeeColony', ({'x': 1.1489461183128191, 'y': 0}, (5.289477553045166, 0))),
	('NelderMead', ({'x': 5.5438690185546875, 'y': -12}, (17.293342096641783, 0))),
	('Hyperband', ({'x': 7.534649421992623, 'y': 3}, (18.055060613166553, 0))),
	('Sobol', ({'x': 9.456933593749998, 'y': 0}, (19.374501579830856, 0))),
	('OptunityOptimizer', ({'x': 9.480038915947556, 'y': 1}, (19.374823892112662, 0))),
	('ParticleSwarm', ({'x': 9.532494333566397, 'y': -2}, (19.463592918993786, 0)))
])
#and another 100 iters
OrderedDict([
	('SKOptBayesian', ({'x': 0.0, 'y': 0}, (0.0, 0))),
	('Bayessian', ({'x': 0.0, 'y': 0}, (0.0, 0))),
	('MSRSM', ({'x': 1.965467987101057e-12, 'y': 0}, (9.71667191151937e-12, 0))),
	('Gutmann', ({'x': 2.0657213945897996e-12, 'y': 0}, (1.021183138050219e-11, 0))),
	('PySHAC', ({'x': 1.0736838586310893, 'y': 1}, (2.596181028196405, 0))),
	('TPE', ({'x': 1.112228671531816, 'y': 1}, (2.9484847125586415, 0))),
	('SKOptForest', ({'x': 1.9743490825396586, 'y': 4}, (4.101231423607379, 0))),
	('SKOptGBTree', ({'x': 1.9730793645346538, 'y': 4}, (4.101344227347713, 0))),
	('BeeColony', ({'x': 1.1480878788645177, 'y': 2}, (4.137194813288049, 0))),
	('HyperEngineBayessian', ({'x': 0.017184911830446792, 'y': -1}, (4.339052002416813, 0))),
	('HyperEnginePortfolio', ({'x': 0.039186794853671714, 'y': 1}, (4.357466574344844, 0))),
	('Yabox', ({'x': 0.10064054071073808, 'y': 1}, (4.483456305012673, 0))),
	('GPyOptOptimizer', ({'x': 1.4703357597723614, 'y': 2}, (4.514562543000367, 0))),
	('Random', ({'x': 0.8303208100740211, 'y': 2}, (5.321946188711948, 0))),
	('NelderMead', ({'x': 5.5438690185546875, 'y': -12}, (17.293342096641783, 0))),
	('Hyperband', ({'x': 7.534649421992623, 'y': 3}, (18.055060613166553, 0))),
	('ParticleSwarm', ({'x': 9.53042265695655, 'y': 7}, (19.243508799760164, 0))),
	('OptunityOptimizer', ({'x': 9.476953125, 'y': -2}, (19.443113499744367, 0))),
	('Sobol', ({'x': 9.553613281249998, 'y': -2}, (19.456426287512052, 0)))
])

OrderedDict([
	('SKOptBayesian', ({'x': 0.0, 'y': 0, 'z': 3}, (0.0, 0))),
	('MSRSM', ({'x': 0.0, 'y': 0, 'z': 3}, (0.0, 0))),
	('GPyOptOptimizer', ({'x': 0.0, 'y': 0, 'z': 3}, (0.0, 0))),
	('Bayessian', ({'x': 0.0, 'y': 0, 'z': 3}, (0.0, 0))),
	('Gutmann', ({'x': 1.862587834282002e-12, 'y': 0, 'z': 3}, (9.208189766241048e-12, 0))),
	('SKOptGBTree', ({'x': 0.0006981287251917047, 'y': 0, 'z': 3}, (0.0034597748341651524, 0))),
	('TPE', ({'x': 0.04262838182879991, 'y': 0, 'z': 3}, (0.24175273938686326, 0))),
	('PySHAC', ({'x': 0.9095346430312279, 'y': 1, 'z': 3}, (2.4508629369328156, 0))),
	('SKOptForest', ({'x': 1.975551753738029, 'y': 4, 'z': 3}, (4.1012335626387895, 0))),
	('HyperEnginePortfolio', ({'x': 0.6955663900186637, 'y': 0, 'z': 3}, (4.135877638966221, 0))),
	('HyperEngineBayessian', ({'x': 0.029900210748344813, 'y': 1, 'z': 3}, (4.347401328753184, 0))),
	('Yabox', ({'x': 0.0842280390688326, 'y': 1, 'z': 3}, (4.4407866406914, 0))),
	('Random', ({'x': 0.1937494360579084, 'y': -1, 'z': 3}, (4.936616103474133, 0))),
	('BeeColony', ({'x': 2.2022165228712076, 'y': 5, 'z': 3}, (5.078197918216663, 0))),
	('Hyperband',({'x': 5.652646139447696, 'y': -7, 'z': 3}, (16.808037852272676, 0))),
	('NelderMead', ({'x': 5.482275009155273, 'y': -48, 'z': 3}, (19.01645084709497, 0))),
	('OptunityOptimizer', ({'x': 9.4734375, 'y': 0, 'z': 3}, (19.392915479901454, 0))),
	('ParticleSwarm', ({'x': 9.572687738918628, 'y': -11, 'z': 3}, (19.629448159563655, 0))),
	('Sobol', ({'x': 9.476269531249997, 'y': -20, 'z': 3}, (19.801833074160353, 0)))
])
```

</details>


The backends are available directly in UniOpt package, and you can enumerate them

```python
for optimizer in UniOpt:
	print("optimizer: " + optimizer.__name__)
```

Here we choose hyperopt's tree of Parzen estimators:
```python
import UniOpt
optimizer=UniOpt.TPE
```


1. Specify a search space. We use the term `spec` for this specification. The spec is a flat `Mapping`-compatible object. It consists of:
	* `HyperparamDefinition` objects. `HyperDef` alias is available. For the help on it see its docstring, here is the brief guide:
	
		* the first arg is the data type, `int` or `float`.
		
		* the second one is a distribution from `scipy.stats`. Yes, we are tied tightly to `scipy`. No, I have no plans to change it for now, we use `scipy` internally for the case the optimizer doesn't have this distribution implemented internally, and even if it has, it is very likely it uses `scipy`. I could create an own registry of distributions to get rid of **mandatory** `scipy`, but this unneedly complicates the things since I would have to maintain it and to write convertors from them to optimizer-specific specs, and most likely I will still use `scipy` for them. If you are not OK with this, post your ideas into the corresponding issue. A couple of words about some special distributions:
			* `uniform` assumes that there is  **SOME smooth enough** relation between a number and the value of a function. You (and the surrogate model) can somehow predict the effect of changing this variable on the loss.
			* `randint` assumes that there is **NO smooth enough** relation between a number and the value of a function. Changing this variable anyhow makes the result be changing unpredictably.
	
	* scalars: `str`ings and numbers
	* `tuple`s and `list`s of scalars. It represents a categorical variable. If you need nonuniformly distributed categories, you have to use the appropriate `scipy.stats` distribution and convert a number into a category yourself.
	* other objects. They can be processed by a backend if this is implemented.

```python
import scipy.stats
from UniOpt.core.Spec import *
spaceSpec={
	"x": HyperDef(float, scipy.stats.uniform(loc=0, scale=10)),
	"y": HyperDef(int, scipy.stats.uniform(loc=0, scale=10)),
	"z": HyperDef(float, scipy.stats.norm(loc=0, scale=10)), #discrete
	"w": 3,
	"v": (0, 1)
}
```

2. Create the function you wanna optimize. It takes a dict of hyperparams and returns **a tuple `(mean, variance)`** of the target function, use variance of `0` if the variance is unknown or not present. Variance is useful for some optimizers and may be available in some crossvalidation routines.

```python
import numpy as np
def optimizee(hyperparamsDict:typing.Mapping[str, typing.Any]):
	return (np.sum(np.array(tuple(hyperparamsDict.values()))**2), 0)
```

3. If you wanna resumption, create a `PointsStorage` object.
    `from UniOpt.core.PointsStorage imporrt *`
    a) `stor=MemoryStorage()` for storing in an array
    b) `stor=SQLiteStorage("Points.sqlite")` for storing in a SQLite DB.

3. Create an optimizer object.

```python
opt = optimizer(optimizee, spaceSpec, iters=100, pointsStorage=stor)
```

4. Call it. You will get the minimal value of your hyperparams. If you provided it with a link to points storage, and injection of points is implemented for the backend you use, it will load points from the storage, so you can transfer progress between optimizers. This will result in a metaoptimizer somewhen. And it will save all the probed points into the storage too.
```python
res=opt()
```

5. Optimizer-specific result (usually the optimizer object) is available via `details` field.
```python
opt.details
```


Implementing an own backend
---------------------------
See [Contributing.md](./Contributing.md).


Implemented backends
--------------------

The backends for following libraries have been implemented:

|Name, link|License|PyPi|Build status|Coverage|Docs|Misc|
|----------|-------|----|------------|--------|----|----|
|[Hyperopt](https://github.com/hyperopt/hyperopt)|![Licence](https://img.shields.io/github/license/hyperopt/hyperopt.svg)|[![PyPi Status](https://img.shields.io/pypi/v/hyperopt.svg)](https://pypi.org/project/hyperopt)|[![Build status](https://github.com/hyperopt/hyperopt/actions/workflows/build.yml/badge.svg)](https://github.com/hyperopt/hyperopt/actions/workflows/build.yml)||https://hyperopt.github.io/hyperopt/|[![Conda package](https://anaconda.org/conda-forge/hyperopt/badges/version.svg)](https://anaconda.org/conda-forge/hyperopt)|
|[hyperband](https://github.com/zygmuntz/hyperband) (no official package, backend imports `hyperband.py`)|[![PROPRIETARY license](https://img.shields.io/badge/license-Proprietary-F00.svg)](https://github.com/zygmuntz/hyperband/blob/master/LICENSE)||||
|[hyperengine](https://github.com/maxim5/hyper-engine.git)|![Licence](https://img.shields.io/github/license/maxim5/hyper-engine.svg)|[![PyPi Status](https://img.shields.io/pypi/v/hyperengine.svg)](https://pypi.org/project/hyperengine)|[![TravisCI Build Status](https://travis-ci.org/maxim5/hyper-engine.svg?branch=master)](https://travis-ci.org/maxim5/hyper-engine)|
|[GPyOpt](https://github.com/SheffieldML/GPyOpt)|![Licence](https://img.shields.io/github/license/SheffieldML/GPyOpt.svg)|[![PyPi Status](https://img.shields.io/pypi/v/gpyopt.svg)](https://pypi.org/project/gpyopt)|[![Build Status](https://travis-ci.org/SheffieldML/GPyOpt.svg?branch=master)](https://travis-ci.org/SheffieldML/GPyOpt)|[![CodeCov Coverage](http://codecov.io/github/SheffieldML/GPyOpt/coverage.svg?branch=master)](http://codecov.io/github/SheffieldML/GPyOpt?branch=master)|[![Read The Docs](https://readthedocs.org/projects/gpyopt/badge/)](https://readthedocs.org/projects/gpyopt/)
|[scikit-optimize](https://github.com/scikit-optimize/scikit-optimize)|![Licence](https://img.shields.io/github/license/scikit-optimize/scikit-optimize.svg)|[![PyPi Status](https://img.shields.io/pypi/v/scikit-optimize.svg)](https://pypi.org/project/scikit-optimize)|[![Travis Build Status](https://travis-ci.org/scikit-optimize/scikit-optimize.svg?branch=master)](https://travis-ci.org/scikit-optimize/scikit-optimize)||https://scikit-optimize.github.io/|[![Conda package](https://anaconda.org/conda-forge/scikit-optimize/badges/version.svg)](https://anaconda.org/conda-forge/scikit-optimize)[![CircleCI Build Status](https://circleci.com/gh/scikit-optimize/scikit-optimize/tree/master.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/scikit-optimize/scikit-optimize)[![Zenodo DOI](https://zenodo.org/badge/54340642.svg)](https://zenodo.org/badge/latestdoi/54340642)
|[SMAC](https://github.com/automl/SMAC3)|![Licence](https://img.shields.io/github/license/automl/SMAC3.svg)||[![Build status](https://github.com/automl/SMAC3/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/automl/SMAC3/actions/workflows/pytest.yml)|[![Codecov Coverage](https://codecov.io/gh/automl/SMAC3/branch/development/graph/badge.svg)](https://codecov.io/gh/automl/SMAC3)|https://automl.github.io/SMAC3/|[![Code Health](https://landscape.io/github/automl/SMAC3/development/landscape.svg?style=flat)](https://landscape.io/github/automl/SMAC3/development)|
|[ECABC](https://github.com/ECRL/ecabc)|![Licence](https://img.shields.io/github/license/ECRL/ecabc.svg)|[![PyPi Status](https://img.shields.io/pypi/v/ECabc.svg)](https://pypi.org/project/ECabc)|
|[optunity](https://github.com/claesenm/optunity)|![Licence](https://img.shields.io/github/license/claesenm/optunity.svg)|[![PyPi Status](https://img.shields.io/pypi/v/Optunity.svg)](https://pypi.org/project/Optunity)|[![Build Status](https://travis-ci.org/claesenm/optunity.svg?branch=master)](https://travis-ci.org/claesenm/optunity)||[![Read The Docs](https://readthedocs.org/projects/optunity/badge/)](https://readthedocs.org/projects/optunity/)|
|[Yabox](https://github.com/pablormier/yabox)|![Licence](https://img.shields.io/github/license/pablormier/yabox.svg)|[![PyPi Status](https://img.shields.io/pypi/v/yabox.svg)](https://pypi.org/project/yabox)||||[![Zenodo DOI](https://zenodo.org/badge/97233963.svg)](https://zenodo.org/badge/latestdoi/97233963)|
|[PySHAC](https://github.com/titu1994/pyshac)|![Licence](https://img.shields.io/github/license/titu1994/pyshac.svg)|[![PyPi Status](https://img.shields.io/pypi/v/pyshac.svg)](https://pypi.org/project/pyshac)|[![Build Status](https://travis-ci.org/titu1994/pyshac.svg?branch=master)](https://travis-ci.org/titu1994/pyshac)|[![Codecov Coverage](https://codecov.io/gh/titu1994/pyshac/branch/master/graph/badge.svg)](https://codecov.io/gh/titu1994/pyshac)|https://titu1994.github.io/pyshac/|
|[RBFOpt](https://github.com/coin-or/rbfopt)|![Licence](https://img.shields.io/github/license/coin-or/rbfopt.svg)|[![PyPi Status](https://img.shields.io/pypi/v/rbfopt.svg)](https://pypi.org/project/rbfopt)|||||[![Read The Docs](https://readthedocs.org/projects/rbfopt/badge/)](https://rbfopt.readthedocs.io/en/latest/)
|[fmfn/BayesianOptimization](https://github.com/fmfn/BayesianOptimization)|![Licence](https://img.shields.io/github/license/fmfn/BayesianOptimization.svg)|[![PyPi Status](https://img.shields.io/pypi/v/bayesian-optimization.svg)](https://pypi.org/project/bayesian-optimization)|[![TravisCI Build Status](https://img.shields.io/travis/fmfn/BayesianOptimization/master.svg)](https://travis-ci.org/fmfn/BayesianOptimization)|[![Codecov Coverage](https://codecov.io/github/fmfn/BayesianOptimization/badge.svg?branch=master&service=github)](https://codecov.io/github/fmfn/BayesianOptimization?branch=master)
|[pySOT](https://github.com/dme65/pySOT)|![Licence](https://img.shields.io/github/license/dme65/pySOT.svg)|[![PyPi Status](https://img.shields.io/pypi/v/pySOT.svg)](https://pypi.org/project/pySOT)|[![TravisCI Build Status](https://img.shields.io/travis/dme65/pySOT/master.svg)](https://travis-ci.org/dme65/pySOT)|[![Codecov Coverage](https://codecov.io/github/dme65/pySOT/badge.svg?branch=master&service=github)](https://codecov.io/github/dme65/pySOT?branch=master) |[![Read The Docs](https://readthedocs.org/projects/pysot/badge/?version=latest)](http://pysot.readthedocs.io/en/latest/?badge=latest)|[![Zenodo DOI](https://zenodo.org/badge/36836292.svg)](https://zenodo.org/badge/latestdoi/36836292)
|[RoBO](https://github.com/automl/RoBO)|![Licence](https://img.shields.io/github/license/automl/RoBO.svg)|[![PyPi Status](https://img.shields.io/pypi/v/RoBO.svg)](https://pypi.org/project/RoBO)|[![TravisCI Build Status](https://img.shields.io/travis/automl/RoBO/master.svg)](https://travis-ci.org/automl/RoBO)|[![Coveralls Coverage](https://coveralls.io/repos/github/automl/RoBO/badge.svg?branch=master)](https://coveralls.io/github/automl/RoBO?branch=master)|https://automl.github.io/RoBO/|[![Landscape Health](https://landscape.io/github/automl/RoBO/master/landscape.svg?style=flat)](https://landscape.io/github/automl/RoBO/master)
|~~[SOpt](https://github.com/Lyrichu/sopt)~~|![Licence](https://img.shields.io/github/license/Lyrichu/sopt.svg)|[![PyPi Status](https://img.shields.io/pypi/v/sopt.svg)](https://pypi.org/project/sopt)||||Calls the same target function even if unneeded
|[BayTune / BTB](https://github.com/HDI-Project/BTB)|![Licence](https://img.shields.io/github/license/HDI-Project/BTB.svg)|[![PyPi Status](https://img.shields.io/pypi/v/baytune.svg)](https://pypi.org/project/baytune)|[![TravisCI Build Status](https://img.shields.io/travis/HDI-Project/BTB/master.svg)](https://travis-ci.org/HDI-Project/BTB)|[![CodeCov Coverage](https://codecov.io/github/HDI-Project/BTB/coverage.svg?branch=master)](https://codecov.io/github/HDI-Project/BTB/)|https://hdi-project.github.io/BTB/|
