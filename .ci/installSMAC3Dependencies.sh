apt-get -y install python3-pybind11;
if pip3 show smac; then :;
else
  apt-get -y install pybind11-dev;
  git clone --depth=1 --branch development https://github.com/automl/SMAC3.git;
  pip3 install --user --upgrade --pre ./SMAC3;
fi;
