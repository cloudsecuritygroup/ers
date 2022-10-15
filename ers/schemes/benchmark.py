##
## Copyright 2022 Zachary Espiritu and Evangelia Anna Markatou and
##                Francesca Falzon and Roberto Tamassia and William Schor
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##

from .common.emm_engine import EMMEngine
from .common.emm import EMM
from ..structures.point import Point
from ..structures.point_3d import Point3D

from .range_brc import RangeBRC
from .range_brc_3d import RangeBRC3D

from .qdag_src import QdagSRC
from .qdag_src_3d import QdagSRC3D

from .linear import Linear,Linear3D

from .quad_brc import QuadBRC
from .quad_brc_3d import QuadBRC3D

from .tdag_src import TdagSRC
from .tdag_src_3d import TdagSRC3D


from ..util.crypto import SecureRandom

from typing import *
from math import ceil, log
from collections import defaultdict
from itertools import accumulate
import secrets
import itertools
import argparse
import json
import random
import time
import sys
from tqdm import tqdm
import pickle

import matplotlib.pyplot as plt

Multimap = Dict[Point, List[bytes]]

BOUND_X = 2 ** 3
BOUND_Y = 2 ** 3
DOC_LENGTH = 10
NUM_QUERIES = 100
NUM_PROCESSES = 16


def next_power_of_2(x):
    return 1 if x == 0 else 2 ** (x - 1).bit_length()


def points_to_multimap(pts: List[List[int]]):
    mm = defaultdict(list)

    max_x = 0
    max_y = 0
    for x, y in pts:
        mm[Point(x, y)].append(bytes(str(x) + " " + str(y), 'utf-8'))
        if x > max_x:
            max_x = x
        if y > max_y:
            max_y = y
    x_size, y_size = next_power_of_2(max_x), next_power_of_2(max_y)
    bound = max(x_size, y_size)
    return mm, bound


def points_3d_to_multimap(pts: List[List[int]]):
    mm = defaultdict(list)

    max_x = 0
    max_y = 0
    max_z = 0
    for x, y, z in pts:
        mm[Point3D(x, y, z)].append(bytes(str(x) + " " + str(y)+ " " + str(z), 'utf-8'))
        if x > max_x:
            max_x = x
        if y > max_y:
            max_y = y
        if z > max_z:
            max_z = z
    x_size, y_size, z_size = next_power_of_2(max_x), next_power_of_2(max_y), next_power_of_2(max_z)
    bound = max(x_size, y_size, z_size)
    return mm, bound


def generate_random_database(
    bound_x: int, bound_y: int, num_elts: int, bound_document_length: int
) -> Multimap:
    """
    Generates a random database with num_elts elements in the
    domain [0, bound_x) * [0, bound_y).
    """

    mm = defaultdict(list)
    for index in range(num_elts):
        pt = generate_random_point(bound_x, bound_y)
        data = SecureRandom(bound_document_length)
        mm[pt].append(data)

    return mm, bound_x


def generate_dense_database(
    bound_x: int, bound_y: int, bound_document_length: int
) -> Multimap:
    """
    Generates a random database with num_elts elements in the
    domain [0, bound_x) * [0, bound_y).
    """

    mm = defaultdict(list)
    pairs = itertools.product(range(bound_x), range(bound_y))

    for x, y in pairs:
        pt = Point(x, y)
        data = SecureRandom(bound_document_length)
        mm[pt].append(data)

    return mm, bound_x, bound_y


def generate_random_point(bound_x: int, bound_y: int) -> Point:
    return Point(secrets.randbelow(bound_x), secrets.randbelow(bound_y))
def generate_random_3d_point(bound_x: int, bound_y: int, bound_z: int) -> Point3D:
    return Point3D(secrets.randbelow(bound_x), secrets.randbelow(bound_y), secrets.randbelow(bound_z))


def generate_random_query(bound_x: int, bound_y: int) -> Tuple[Point, Point]:
    p1 = generate_random_point(bound_x, bound_y)
    p2 = generate_random_point(bound_x, bound_y)

    # Guarantee that query satisfies "dominates" assumption:
    if p1.x > p2.x:
        p1.x, p2.x = p2.x, p1.x
    if p1.y > p2.y:
        p1.y, p2.y = p2.y, p1.y

    return (p1, p2)

def generate_random_small_query(bound_x: int, bound_y: int) -> Tuple[Point, Point]:
    p1 = generate_random_point(bound_x-1, bound_y-1)
    p2 = Point(random.randint(p1.x, min(int(p1.x+bound_x*0.3),bound_x-1)), random.randint(p1.y, min(int(p1.y+bound_y*0.3),bound_y-1)))
    #print(p1,p2)
    # Guarantee that query satisfies "dominates" assumption:
    if p1.x > p2.x:
        p1.x, p2.x = p2.x, p1.x
    if p1.y > p2.y:
        p1.y, p2.y = p2.y, p1.y

    return (p1, p2)

def generate_random_target_query(bound_x: int, bound_y: int, target:int) -> Tuple[Point, Point]:
    p1 = generate_random_point(int(bound_x*(1-(target**0.5)*0.01)), int(bound_y*(1-(target**0.5)*0.01)))


    p2 = Point(min(random.randint(p1.x, p1.x+ int(bound_x*target*0.03)),bound_x-1), min(random.randint(p1.y, p1.y+ int(bound_y*target*0.03)),bound_y-1))

    #print(p1,p2)
    # Guarantee that query satisfies "dominates" assumption:
    if p1.x > p2.x:
        p1.x, p2.x = p2.x, p1.x
    if p1.y > p2.y:
        p1.y, p2.y = p2.y, p1.y

    return (p1, p2)

def generate_random_3d_query(bound_x: int, bound_y: int, bound_z: int) -> Tuple[Point3D, Point3D]:
    p1 = generate_random_3d_point(bound_x, bound_y, bound_z)
    p2 = generate_random_3d_point(bound_x, bound_y, bound_z)

    # Guarantee that query satisfies "dominates" assumption:
    if p1.x > p2.x:
        p1.x, p2.x = p2.x, p1.x
    if p1.y > p2.y:
        p1.y, p2.y = p2.y, p1.y
    if p1.z > p2.z:
        p1.z, p2.z = p2.z, p1.z

    return (p1, p2)


# note: include token db for storage measurement for DPRF


def run_benchmarks(schemes, datasets, run_query, benchmark):
    
    storage_results = defaultdict(list)
    query_size_results = defaultdict(list)
    query_gen_time_results = defaultdict(list)
    server_handling_time_results = defaultdict(list)
    false_positive_results = defaultdict(list)
    decryption_results = defaultdict(list)

    i = 0
    for ds, bound in datasets:
        is_2d_database = isinstance(list(ds.keys())[0], Point)
        if is_2d_database:
            print(f"2d database: {bound} x {bound}")
        else:
            print(f"3d database: {bound} x {bound} x {bound}")

        bucks = defaultdict(list)
        ten_bucks = defaultdict(list)

        if is_2d_database:
            for ps in tqdm(range(NUM_QUERIES*10000)):
                p1, p2 = generate_random_query(bound, bound)
                range_size = (p2.x - p1.x+1) * (p2.y - p1.y+1)
                percent_bucket = (int(100* range_size / (bound * bound)))
                ten_bucks[10*int(percent_bucket/10)].append((p1,p2))
                bucks[percent_bucket].append((p1,p2))
        else:
            for ps in tqdm(range(NUM_QUERIES*100000)):
                p1, p2 = generate_random_3d_query(bound, bound, bound)
                range_size = (p2.x - p1.x) * (p2.y - p1.y) * (p2.z - p1.z)
                percent_bucket = (int(100* range_size / (bound * bound*bound)))
                ten_bucks[10*int(percent_bucket/10)].append((p1,p2))
                bucks[percent_bucket].append((p1,p2))


        if 100 in ten_bucks:
            del ten_bucks[100]
        for jk in sorted(ten_bucks):
            ten_bucks[jk] = ten_bucks[jk][:NUM_QUERIES]


        new_bucks = {}
        for jk in range(25):
            new_bucks[jk] = bucks[jk][:NUM_QUERIES]
        #exit()

                            
        for scheme in schemes:
            print(str(scheme.__name__))

            t0 = time.time_ns()
            print("Building index...")
            s = scheme(EMMEngine(bound, bound))
            key = s.setup(16)
            s.build_index(key, ds)
            t1 = time.time_ns()

            total_time = t1 - t0
            print("Took", total_time, "ns")

            # FALSE POSITIVE COMPARISON
            if False:
                if is_2d_database:
                    false_positive_s = LogarithmicSSE(EMMEngine(bound, bound))
                    false_positive_key = false_positive_s.setup(16)
                    false_positive_s.build_index(false_positive_key, ds)
                else:
                    false_positive_s = LogarithmicSSE3D(EMMEngine(bound, bound))
                    false_positive_key = false_positive_s.setup(16)
                    false_positive_s.build_index(false_positive_key, ds)

            print("Accumulating storage results...")
            encrypted_db_size = sum(
                        (
                            sys.getsizeof(k) + sys.getsizeof(v)
                            for k, v in s.encrypted_db.items()
                        )
                    )

            if run_query:
                print("Running query benchmarks!...")
                if i == len(datasets) - 1:
                    # run some bandwidth benchmarks on the biggest database
                    if is_2d_database:
                        TOTAL_DOMAIN_POINTS = bound * bound
                    else:
                        TOTAL_DOMAIN_POINTS = bound * bound

                    def do_query_benchmark(p1, p2,target_bucket):
                        range_size = 0
                        if is_2d_database:
                            range_size = (p2.x - p1.x) * (p2.y - p1.y)
                        else:
                            range_size = (p2.x - p1.x) * (p2.y - p1.y) * (p2.z - p1.z)

                        t0 = time.time_ns()
                        to_be_sent = s.trapdoor(key, p1, p2)
                        t1 = time.time_ns()
                        trapdoor_time = t1 - t0
                        #print("trapdoor_time", trapdoor_time)

                        #print("tokens", len(to_be_sent), to_be_sent)

                        total_token_size = 0
                        if isinstance(to_be_sent, list):
                            total_token_size = print(
                                sum((sys.getsizeof(r) for r in list(to_be_sent))),
                                to_be_sent,
                            )
                        else:
                            total_token_size = sys.getsizeof(to_be_sent)

                        #print("total_token_size", total_token_size)

                        t0 = time.time_ns()
                        #print(p1,p2)
                        results = s.search(to_be_sent)
                        t1 = time.time_ns()
                        handling_time = t1 - t0

                        #print("res", len(results))


                        t0 = time.time_ns()
                        data = s.resolve(key, results)
                        t1 = time.time_ns()
                        decryption_time = t1 - t0

                        #print("handling_time", handling_time)
                        storage_results[target_bucket].append(len(results))
                        query_size_results[target_bucket].append(total_token_size)
                        query_gen_time_results[target_bucket].append(trapdoor_time)
                        server_handling_time_results[target_bucket].append(
                            handling_time
                        )
                        decryption_results[target_bucket].append(decryption_time)


                    start = time.time()

                    #do_query_benchmark(Point(0,0), Point(7,7) ,100)
                    #exit()

                    if benchmark=="small":
                        for target_bucket in tqdm(range(0,10)):
                            #print(target_bucket)
                            for (p1,p2) in new_bucks[target_bucket]:
                                #print(p1,p2)
                                do_query_benchmark(p1, p2,target_bucket)

                    elif benchmark=="all":
                        for i in tqdm(range(0,NUM_QUERIES)):
                            do_query_benchmark(Point(0,0), Point(bound-2,bound-2) ,100)

                    else:
                        for target_bucket in tqdm(range(0,99,10)):
                            #print(target_bucket)
                            for (p1,p2) in ten_bucks[target_bucket]:
                                do_query_benchmark(p1, p2,target_bucket)


                    

                    end = time.time()


                    print("Getting ", NUM_QUERIES, "queries took ", end -start )
        i += 1

    print("Done.")
    print("IndexSizeBytes,ConstructTimeNS")
    for scheme in schemes:
        name = scheme.__name__
        print(f"{encrypted_db_size},{total_time}")
        print("----")
        print("PercentOfDomain,Average Query Time (sec)")
        for bucket, sizes in query_gen_time_results.items():
            print(f"{bucket},{(sum(sizes) / len(sizes))/10**9}")
        print("----")
        print("PercentOfDomain, Average Eval Time (sec)")
        for bucket, sizes in server_handling_time_results.items():
            print(f"{bucket},{(sum(sizes) / len(sizes))/10**9}")
        print("----")
        print("PercentOfDomain,Average Result Count ")
        for bucket, sizes in storage_results.items():
            print(f"{bucket},{sum(sizes) / len(sizes)}")
        print("----")
        print("PercentOfDomain,Average Result Time (sec)")
        for bucket, sizes in decryption_results.items():
            print(f"{bucket},{(sum(sizes) / len(sizes))/10**9}")

    return (
        storage_results,
        query_size_results,
        query_gen_time_results,
        server_handling_time_results,
    )


def running_avg(numbers):
    for count in range(1, len(numbers) + 1):
        yield sum(numbers[:count]) / count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parameters for attack")
    parser.add_argument("dataset", nargs="?", default=None)
    parser.add_argument("num_records", nargs="?", default=None)
    parser.add_argument("scheme_name", nargs="?", default=None)
    parser.add_argument("run_query", nargs="?", default=None)
    parser.add_argument("num_queries", nargs="?", default=None)
    parser.add_argument("benchmark", nargs="?", default=None)
    args = parser.parse_args()

    data_file = args.dataset
    datasets = []

    NUM_QUERIES = int(args.num_queries)
    print("NUM_QUERIES", NUM_QUERIES)
    if "pickle" in data_file:
        with open(data_file, 'rb') as f:
            dpts = pickle.load(f)


        pts = []

        if "gowalla_" in data_file or "spitz" in data_file:
            pts = dpts
        else:
            for i in dpts:
                for j in range(dpts[i]):
                    pts.append(i)
    else:
        with open(data_file) as fp:
            pts = json.load(fp)

    num_dims = len(pts[0])

    if int(args.num_records) == -1:
        args.num_records = len(pts)

    if num_dims == 2:
        datasets.append(points_to_multimap(random.sample(pts, int(args.num_records))))
    elif num_dims == 3:
        datasets.append(points_3d_to_multimap(pts[0 : int(args.num_records)]))

    scheme_dict = {
        "range_brc": RangeBRC,
        "range_brc_3d": RangeBRC3D,
        "linear": Linear,
        "linear_3d": Linear3D,
        "qdag_src": QdagSRC,
        "qdag_src_3d": QdagSRC3D,
        "quad_brc": QuadBRC,
        "quad_brc_3d": QuadBRC3D,
        "tdag_src":TdagSRC,
        "tdag_src_3d":TdagSRC3D,

    }
    schemes = [scheme_dict[args.scheme_name]]

    is_run_query = False
    if args.run_query == "runquery":
        is_run_query = True
    (
        storage_results,
        query_size_results,
        query_gen_time_results,
        server_handling_time_results,
    ) = run_benchmarks(schemes, datasets, is_run_query, args.benchmark)
