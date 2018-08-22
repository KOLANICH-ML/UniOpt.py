if $( python -c "import sys;sys.exit(int(not (sys.version_info < (3, 5)) ))" ); then
 curl -O https://raw.githubusercontent.com/python/cpython/3.6/Lib/typing.py;
 curl -O https://raw.githubusercontent.com/python/cpython/3.5/Lib/linecache.py;
 curl -O https://raw.githubusercontent.com/python/cpython/3.5/Lib/traceback.py;
 #curl -O https://raw.githubusercontent.com/python/cpython/3.5/Lib/importlib/abc.py;
 #curl -O https://raw.githubusercontent.com/python/cpython/3.5/Lib/importlib/_bootstrap_external.py;
 mv ./typing.py ./linecache.py ./traceback.py $PYTHON_MODULES_DIR/
fi;
if $( python -c "import sys;sys.exit(int(not (sys.version_info < (3, 6)) ))" ); then
curl -O https://raw.githubusercontent.com/python/cpython/3.7/Lib/enum.py;
  mv ./enum.py $PYTHON_MODULES_DIR/
fi;
