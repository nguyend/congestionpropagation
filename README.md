# congestionpropagation
Please cite the following paper when using the code, the sample data is aggregated and added random shifts from original one.

Author: Hoang Nguyen

Email: dungbk04@gmail.com

Paper: Nguyen, H., Liu, W. and Chen, F., 2017. Discovering congestion propagation patterns in spatio-temporal traffic data. IEEE Transactions on Big Data, 3(2), pp.169-180.

@article{nguyen2017discovering,
  title={Discovering congestion propagation patterns in spatio-temporal traffic data},
  author={Nguyen, Hoang and Liu, Wei and Chen, Fang},
  journal={IEEE Transactions on Big Data},
  volume={3},
  number={2},
  pages={169--180},
  year={2017},
  publisher={IEEE}
}

The probability estimation is implemented for a tree within a time range, e.g. between 5:00pm and 6:00pm.
For DBN, it is just a bit more specific, e.g. calculate probability of a congested at BA at 5:00pm that lead to CB at 5:05pm then multiply all pairs of a tree together.
In simple work, DBN is BN with time-dependent when you calculate the probability.

Any questions, please let me know.
If you'd like to plot some of the result, please replace gmplot.py in the site-packages with the one included in my folder, then insert your Google Map key (in line 182).
The output frequent tree plot will be saved in mymap.html to view in a web browser.
