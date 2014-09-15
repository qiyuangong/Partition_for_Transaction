Partition_for_Transaction
===========================
Partition_for_Transaction is a top-down anonymization algorithm for set-valued data (or transaction), based on local generalization. It works under k-anonymity constrain, and ensure higher data utility than AA[2]. He et al. proposed this algorithm in 2009[1] on VLDB conference, and gave the pseudocode in his papers, the source code(C++ implement) is not available.

This repository is an *open source python implement* for Partition_for_Transaction. I implement this algorithm in python for further study.

### Motivation 
Researches on data privacy have lasted for more than ten years, lots of great papers have been published. However, only a few open source projects are available on Internet [3-4], most open source projects are using algorithms proposed before 2004! Fewer projects have been used in real life. Worse more, most people even don't hear about it. Such a tragedy! 

I decided to make some effort. Hoping these open source repositories can help researchers and developers on data privacy (privacy preserving data publishing).

## Usage

Run command in your terminal:
	
	# if K is not privoided, then K is set to 10 as default
	python anonymizer.py [K]

## Copyright

by Qiyuan Gong
qiyuangong@gmail.com

2014-09-12

## For more information:

[1]  He, Y. & Naughton, J. F. Anonymization of set-valued data via top-down, local generalization Proc. VLDB Endow., VLDB Endowment, 2009, 2, 934-945

[2] Terrovitis, M.; Mamoulis, N. & Kalnis, P. Local and global recoding methods for anonymizing set-valued data The VLDB Journal, Springer-Verlag New York, Inc., 2011, 20, 83-106

[3] [UTD Anonymization Toolbox](http://cs.utdallas.edu/dspl/cgi-bin/toolbox/index.php?go=home)

[4] [ARX- Powerful Data Anonymization](https://github.com/arx-deidentifier/arx)
