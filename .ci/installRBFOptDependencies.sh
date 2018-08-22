echo "dependencies for rbfopt";
if [ -x $EXECUTABLE_DEPENDENCIES_DIR/bonmin ] && [ -x $EXECUTABLE_DEPENDENCIES_DIR/ipopt ]; then :;
else
  apt-get -y install p7zip-full;
  curl -O https://ampl.com/dl/open/bonmin/bonmin-linux64.zip -O https://ampl.com/dl/open/ipopt/ipopt-linux64.zip;
  7za x bonmin-linux64.zip;
  7za x -y ipopt-linux64.zip;
  mv ./bonmin ./ipopt $EXECUTABLE_DEPENDENCIES_DIR/;
fi;
if pip3 show pyutilib && pip3 show pyomo; then :;
else
  git clone --depth=1 https://github.com/PyUtilib/pyutilib.git;
  git clone --depth=1 https://github.com/Pyomo/pyomo.git;
  pip3 install --user --upgrade --pre ./pyutilib ./pyomo;
fi;
