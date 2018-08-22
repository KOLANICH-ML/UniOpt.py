if pip3 show smac; then :;
else
  source ${BASH_SOURCE%/*}/installCython.sh
  git clone --depth=1 https://github.com/SheffieldML/GPy.git
  find ./GPy -name '*.pyx' -exec cython {} \;
  pip3 install --upgrade --user --pre ./GPy
fi;
