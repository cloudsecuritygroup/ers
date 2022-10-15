# Range Search on Encrypted Multi-Attribute Data: Experiment Code

This is the associated artifact for the paper "Range Search on Encrypted Multi-Attribute Data" by Francesca Falzon, Evangelia Anna Markatou, Zachary Espiritu, and Roberto Tamassia.

**Important:** This repository implements several cryptographic primitives (used for research purposes) which should not be used in production.

## Dependencies 

Our schemes assume prior installation of Python 3.9.0 or above which can be installed from [here](https://www.python.org/downloads/source/).
The `requirements.txt` file in the main directory contains a list of all the necessary dependencies for running our schemes and reproducing our experiments; these dependencies can be installed using the `pip3` command.

## Detailed Usage

### Benchmarking the schemes

We implement the following schemes from our paper:

* **Linear**: A scheme that achieves optimal storage at the expense of query bandwidth.
* **Range-BRC**: A scheme based on the classic range tree data structure and which uses the best range cover (BRC) to minimize the number of search tokens issued while still ensuring that no false positives are returned.
* **Quad-BRC**: A scheme based on the classic quadtree data structure together with the best range cover (BRC). This scheme offers smaller storage requirements compared to Range-BRC in exchange for a larger query bandwidth.
* **Tdag-SRC**: A scheme that extends the Tdag-SRC scheme of Demertzis et al. (SIGMOD 2016) to higher dimensions. This acheives the smallest bandwidth, i.e. a single search token, at the expense of false positives, while achieveing the same asymptotic complexity of the range tree.
* **Qdag-SRC**: A scheme that leverages a novel data structure called a quadtree-liked DAG (QDAG). The QDAG is based on the quadtree but injects additional nodes in such a way that it minimizes the number of false positives when using the single range cover (SRC). It achieves the same asymptotic storage complexity as the Quad-BRC. 

Each of our schemes can be tested on the following four datasets:

* **Gowalla**: A 4D dataset consisting of $6,442,892$ latitude-longitude points of check-ins 
 from users of the  Gowalla social networking website  between  2009 and 2010.
* **Spitz**:  A 2D dataset of $28,837$ latitude-longitude points of phone location data of politician Malte Spitz from Aug 2009 to Feb 2010.
* **NH**: A 3D dataset comprised of $4,096$ elevation points on domain $[2^6] \times [2^6] \times [2^6]$ sampled from the United States Geological Survey's Elevation Data from the White Mountains of New Hampshire. We change the domain size by keeping exactly one aggregated elevation value per latitude and longitude value. 
* **Cali**: A 2D dataset of $21,047$ latitude-longitude points of road network intersections in California.

You can execute our schemes on these datasets by executing the following command from the root directory of the repository:

```
$ bash {spitz.sh, cali.sh, gowalla.sh, nh.sh} {linear, range_brc, quad_brc, tdag_src, qdag_src}
```

For example, if you wish to reproduce our Range-BRC scheme experiments on the California data set, then you should run `$ bash cali.sh range_brc`. Each such command generates builds the index over the appropriate domain size and reports the resulting index size and setup time. Then it generates 100 queries and averages and reports the query response times and query sizes over these 100 queries.

## Appendix

### Our Environment

The experiments in our paper were executed on Brown University's [Oscar](https://docs.ccv.brown.edu/oscar/) compute cluster. Oscar uses the [Slurm](https://slurm.schedmd.com/documentation.html) job scheduler for job submission. Each job consists of an experiment on a single scheme on a single dataset. To our knowledge, assigned cluster resources were exclusive to our jobs during the duration of our experiments (i.e. jobs were not preempted).


### License

All code is provided as-is under the *Apache License 2.0*. See
[`LICENSE`](./LICENSE) for full license text.

Every source code file should be prefixed with a comment containing the following text:

```
Copyright 2022 Zachary Espiritu and Evangelia Anna Markatou and
               Francesca Falzon and Roberto Tamassia and William Schor

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
