cd tools/python-mincut

if [ ! -d 'build/' ]; then
    mkdir build
fi

cd build
cmake .. && make
cd ../../..
