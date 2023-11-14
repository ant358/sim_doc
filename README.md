# Implementation of Shingling, MinHash and LSH  

## Process

![Stanford slides image](docs/process.png "Process Overview")

## Usage
The code requires Python 3.11 and pandas to load the data.
To run with the default test data run `python main.py` from the root directory.
There are command line arguments to change the data source and the number of hash functions used. See main.py for details.

## Next steps  
* To run on a larger dataset. 
* To run in docker
* To run on json data - done
* To add results for different thresholds to the output
* Batch process millions of records keeping the unique ones each time


## References
1. [Web Article with code example](https://www.codemotion.com/magazine/backend/fast-document-similarity-in-python-minhashlsh/)
2. [Stanford Chapter 3 lecture](https://www.youtube.com/watch?v=dRWO3il-jjA)
3. [Starter Notebook](https://github.com/nicoDs96/Document-Similarity-using-Python-and-PySpark/blob/master/LSH/DM_HW2_Ex2.ipynb)
4. [MMDS book](http://infolab.stanford.edu/~ullman/mmds/book.pdf)
5. [MMDS slides](http://www.mmds.org/mmds/v2.1/ch03-lsh.pdf)
