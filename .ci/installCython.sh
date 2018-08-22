if pip3 show cython ; then :;
else
  apt-get -y install swig gcc g++;
  git clone --depth=1 https://github.com/cython/cython.git;
  pip3 install --upgrade --user --pre ./cython;
fi;
