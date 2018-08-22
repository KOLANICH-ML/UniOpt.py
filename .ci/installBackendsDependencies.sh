apt-get update

echo "dependencies for GPyopt"
source ${BASH_SOURCE%/*}/installGPyOptDependencies.sh

echo "dependencies for rbfopt"
source ${BASH_SOURCE%/*}/installRBFOptDependencies.sh

echo "dependencies for SMAC3"
source ${BASH_SOURCE%/*}/installSMAC3Dependencies.sh

if pip3 show ecabc; then :;
else
  git clone --depth=1 --branch _args_fix https://github.com/KOLANICH/ecabc.git
  pip install --user --upgrade --pre ./ecabc
fi;

if [ -f $PYTHON_MODULES_DIR/hyperband.py ] ; then :;
else
  curl -O https://raw.githubusercontent.com/zygmuntz/hyperband/master/hyperband.py
  2to3 -wn hyperband.py
  mv hyperband.py $PYTHON_MODULES_DIR/
fi;

if [ -f $PYTHON_MODULES_DIR/diffevo.py ] ; then :;
else
  curl -O https://raw.githubusercontent.com/tiagoCuervo/EvoFuzzy/4cbfce4a432fd162d6f30017c8de0477b29e5f42/diffevo.py
  2to3 -wn diffevo.py
  mv diffevo.py $PYTHON_MODULES_DIR/
fi;


# RoBo -> george
pip install --upgrade git+https://github.com/yaml/pyyaml.git
