import os
import sys
import concurrent.futures as cf
import functools
import hashlib
import io
import random
import time
from multiprocessing import Pool, cpu_count

import keras
import numpy as np
import pandas as pd
import scipy
import sklearn.metrics

from scipy.stats import rankdata

from dht_prototype.masternode_modules.animecoin_modules.animecoin_dupe_detection import DupeDetector, measure_similarity

pool = Pool(int(round(cpu_count() / 2)))

# requirements: pip install numpy scipy keras pillow sklearn pandas


def get_sha256_hash_of_input_data_func(input_data_or_string):
    if isinstance(input_data_or_string, str):
        input_data_or_string = input_data_or_string.encode('utf-8')
    sha256_hash_of_input_data = hashlib.sha3_256(input_data_or_string).hexdigest()
    return sha256_hash_of_input_data


class MyTimer():
    def __init__(self):
        self.start = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time()
        runtime = end - self.start
        msg = '({time} seconds to complete)'
        print(msg.format(time=round(runtime, 5)))


def get_image_deep_learning_features_combined_vector_for_single_image_func(path_to_art_image_file):
    model_1_image_fingerprint_vector, model_2_image_fingerprint_vector, model_3_image_fingerprint_vector, model_4_image_fingerprint_vector, model_5_image_fingerprint_vector, sha256_hash_of_art_image_file, dupe_detection_model_1, dupe_detection_model_2, dupe_detection_model_3, dupe_detection_model_4, dupe_detection_model_5 = compute_image_deep_learning_features_func(
        path_to_art_image_file)
    model_1_image_fingerprint_vector_clean = [x[0] for x in model_1_image_fingerprint_vector]
    model_2_image_fingerprint_vector_clean = [x[0] for x in model_2_image_fingerprint_vector]
    model_3_image_fingerprint_vector_clean = [x[0] for x in model_3_image_fingerprint_vector]
    model_4_image_fingerprint_vector_clean = [x[0] for x in model_4_image_fingerprint_vector]
    model_5_image_fingerprint_vector_clean = [x[0] for x in model_5_image_fingerprint_vector]
    combined_image_fingerprint_vector = model_1_image_fingerprint_vector_clean + model_2_image_fingerprint_vector_clean + model_3_image_fingerprint_vector_clean + model_4_image_fingerprint_vector_clean + model_5_image_fingerprint_vector_clean
    A = pd.DataFrame([sha256_hash_of_art_image_file, path_to_art_image_file]).T
    B = pd.DataFrame(combined_image_fingerprint_vector).T
    combined_image_fingerprint_df_row = pd.concat([A, B], axis=1, join_axes=[A.index])
    return combined_image_fingerprint_df_row


def list_files(basedir):
    files = []
    for i in os.listdir(basedir):
        if i.split(".")[-1] in ["jpg", "jpeg", "bmp", "gif", "png"]:
            files.append(os.path.join(basedir, i))
            print("ABORTING EARLY FOR SPEED")
            break
    return files


def get_fingerprint_for_file(current_image_file_path, dupedetector, target_size):
    # read the actual image file
    data = open(current_image_file_path, 'rb').read()

    # compute hash
    imghash = get_sha256_hash_of_input_data_func(data)

    # read the actual image file
    image = keras.preprocessing.image.load_img(current_image_file_path, target_size=target_size)

    fingerprints = dupedetector.compute_deep_learning_features(image)
    return imghash, fingerprints


def populate_fingerprint_db(basedir, dupedetector, target_size):
    files = list_files(basedir)
    db = {}
    for current_image_file_path in files:
        print('\nNow adding image file ' + current_image_file_path + ' to image fingerprint database.')

        imghash, fingerprints = get_fingerprint_for_file(current_image_file_path, dupedetector, target_size)

        # add to the database
        db[imghash] = (current_image_file_path, fingerprints)
    return db


def assemble_fingerprints_for_pandas(fingerprint_db):
    pandas_fingerprint_table = pd.DataFrame()
    rows = []
    for current_image_file_hash, data in fingerprint_db.items():
        file_path, fingerprint_collection = data

        # concatenate fingerprints from various models and append it to rows
        combined_fingerprint_vector = []
        for modelname, fingerprints in fingerprint_collection.items():
            print(modelname, type(fingerprints))

            # TODO: this is very expensive
            fingerprint_vector = [x[0] for x in fingerprints]

            combined_fingerprint_vector += fingerprint_vector
        rows.append(combined_fingerprint_vector)

        # create dataframe rows for every image
        df_row = pd.DataFrame([current_image_file_hash, file_path]).T
        pandas_fingerprint_table = pandas_fingerprint_table.append(df_row)

    df_vectors = pd.DataFrame()
    for cnt, _ in enumerate(rows):
        df_vectors = df_vectors.append(pd.DataFrame(rows[cnt]).T)

    final_pandas_table = pd.concat([pandas_fingerprint_table, df_vectors], axis=1,
                                   join_axes=[pandas_fingerprint_table.index])

    return final_pandas_table


def hoeffd_inner_loop_func(i, R, S):
    # See slow_exact_hoeffdings_d_func for definition of R, S
    Q_i = 1 + sum(np.logical_and(R < R[i], S < S[i]))
    Q_i = Q_i + (1 / 4) * (sum(np.logical_and(R == R[i], S == S[i])) - 1)
    Q_i = Q_i + (1 / 2) * sum(np.logical_and(R == R[i], S < S[i]))
    Q_i = Q_i + (1 / 2) * sum(np.logical_and(R < R[i], S == S[i]))
    return Q_i


def slow_exact_hoeffdings_d_func(x, y, pool):
    # Based on code from here: https://stackoverflow.com/a/9322657/1006379
    # For background see: https://projecteuclid.org/download/pdf_1/euclid.aoms/1177730150
    x = np.array(x)
    y = np.array(y)
    N = x.shape[0]
    print('Computing tied ranks...')
    with MyTimer():
        R = scipy.stats.rankdata(x, method='average')
        S = scipy.stats.rankdata(y, method='average')
    if 0:
        print('Computing Q with list comprehension...')
        with MyTimer():
            Q = [hoeffd_inner_loop_func(i, R, S) for i in range(N)]
    print('Computing Q with multiprocessing...')
    with MyTimer():
        hoeffd = functools.partial(hoeffd_inner_loop_func, R=R, S=S)
        Q = pool.map(hoeffd, range(N))
    print('Computing helper arrays...')
    with MyTimer():
        Q = np.array(Q)
        D1 = sum(((Q - 1) * (Q - 2)))
        D2 = sum((R - 1) * (R - 2) * (S - 1) * (S - 2))
        D3 = sum((R - 2) * (S - 2) * (Q - 1))
        D = 30 * ((N - 2) * (N - 3) * D1 + D2 - 2 * (N - 2) * D3) / (N * (N - 1) * (N - 2) * (N - 3) * (N - 4))
    print('Exact Hoeffding D: ' + str(round(D, 8)))
    return D


def generate_bootstrap_sample_func(original_length_of_input, sample_size):
    bootstrap_indices = np.array([random.randint(1, original_length_of_input) for x in range(sample_size)])
    return bootstrap_indices


def compute_average_and_stdev_of_25th_to_75th_percentile_func(input_vector):
    input_vector = np.array(input_vector)
    percentile_25 = np.percentile(input_vector, 25)
    percentile_75 = np.percentile(input_vector, 75)
    trimmed_vector = input_vector[input_vector > percentile_25]
    trimmed_vector = trimmed_vector[trimmed_vector < percentile_75]
    trimmed_vector_avg = np.mean(trimmed_vector)
    trimmed_vector_stdev = np.std(trimmed_vector)
    return trimmed_vector_avg, trimmed_vector_stdev


def compute_bootstrapped_hoeffdings_d_func(x, y, pool, sample_size):
    x = np.array(x)
    y = np.array(y)
    assert (x.size == y.size)
    original_length_of_input = x.size
    bootstrap_sample_indices = generate_bootstrap_sample_func(original_length_of_input - 1, sample_size)
    N = sample_size
    x_bootstrap_sample = x[bootstrap_sample_indices]
    y_bootstrap_sample = y[bootstrap_sample_indices]
    R_bootstrap = scipy.stats.rankdata(x_bootstrap_sample)
    S_bootstrap = scipy.stats.rankdata(y_bootstrap_sample)
    hoeffdingd = functools.partial(hoeffd_inner_loop_func, R=R_bootstrap, S=S_bootstrap)
    Q_bootstrap = pool.map(hoeffdingd, range(sample_size))
    Q = np.array(Q_bootstrap)
    D1 = sum(((Q - 1) * (Q - 2)))
    D2 = sum((R_bootstrap - 1) * (R_bootstrap - 2) * (S_bootstrap - 1) * (S_bootstrap - 2))
    D3 = sum((R_bootstrap - 2) * (S_bootstrap - 2) * (Q - 1))
    D = 30 * ((N - 2) * (N - 3) * D1 + D2 - 2 * (N - 2) * D3) / (N * (N - 1) * (N - 2) * (N - 3) * (N - 4))
    return D


def compute_parallel_bootstrapped_bagged_hoeffdings_d_func(x, y, sample_size, number_of_bootstraps, pool):
    def apply_bootstrap_hoeffd_func(ii):
        verbose = 0
        if verbose:
            print('Bootstrap ' + str(ii) + ' started...')
        return compute_bootstrapped_hoeffdings_d_func(x, y, pool, sample_size)

    list_of_Ds = list()
    with cf.ThreadPoolExecutor() as executor:
        inputs = range(number_of_bootstraps)
        for result in executor.map(apply_bootstrap_hoeffd_func, inputs):
            list_of_Ds.append(result)
    robust_average_D, robust_stdev_D = compute_average_and_stdev_of_25th_to_75th_percentile_func(list_of_Ds)
    return list_of_Ds, robust_average_D, robust_stdev_D


def calculate_randomized_dependence_coefficient_func(x, y, f=np.sin, k=20, s=1 / 6., n=1):
    if n > 1:  # Note: Not actually using this because it gives errors constantly.
        values = []
        for i in range(n):
            try:
                values.append(calculate_randomized_dependence_coefficient_func(x, y, f, k, s, 1))
            except np.linalg.linalg.LinAlgError:
                pass
        return np.median(values)
    if len(x.shape) == 1: x = x.reshape((-1, 1))
    if len(y.shape) == 1: y = y.reshape((-1, 1))
    cx = np.column_stack([rankdata(xc, method='ordinal') for xc in x.T]) / float(x.size)  # Copula Transformation
    cy = np.column_stack([rankdata(yc, method='ordinal') for yc in y.T]) / float(y.size)
    O = np.ones(cx.shape[0])  # Add a vector of ones so that w.x + b is just a dot product
    X = np.column_stack([cx, O])
    Y = np.column_stack([cy, O])
    Rx = (s / X.shape[1]) * np.random.randn(X.shape[1], k)  # Random linear projections
    Ry = (s / Y.shape[1]) * np.random.randn(Y.shape[1], k)
    X = np.dot(X, Rx)
    Y = np.dot(Y, Ry)
    fX = f(X)  # Apply non-linear function to random projections
    fY = f(Y)
    try:
        C = np.cov(np.hstack([fX, fY]).T)  # Compute full covariance matrix
        k0 = k
        lb = 1
        ub = k
        while True:  # Compute canonical correlations
            Cxx = C[:int(k), :int(k)]
            Cyy = C[k0:k0 + int(k), k0:k0 + int(k)]
            Cxy = C[:int(k), k0:k0 + int(k)]
            Cyx = C[k0:k0 + int(k), :int(k)]
            eigs = np.linalg.eigvals(np.dot(np.dot(np.linalg.inv(Cxx), Cxy), np.dot(np.linalg.inv(Cyy), Cyx)))
            if not (np.all(np.isreal(eigs)) and  # Binary search if k is too large
                    0 <= np.min(eigs) and
                    np.max(eigs) <= 1):
                ub -= 1
                k = (ub + lb) / 2
                continue
            if lb == ub: break
            lb = k
            if ub == lb + 1:
                k = ub
            else:
                k = (ub + lb) / 2
        return np.sqrt(np.max(eigs))
    except:
        return 0.0


def bootstrapped_hoeffd(x, y, sample_size, number_of_bootstraps, pool):
    def apply_bootstrap_hoeffd_func(ii):
        verbose = 0
        if verbose:
            print('Bootstrap ' + str(ii) + ' started...')
        return compute_bootstrapped_hoeffdings_d_func(x, y, pool, sample_size)

    list_of_Ds = list()
    with cf.ThreadPoolExecutor() as executor:
        inputs = range(number_of_bootstraps)
        for result in executor.map(apply_bootstrap_hoeffd_func, inputs):
            list_of_Ds.append(result)
    robust_average_D, robust_stdev_D = compute_average_and_stdev_of_25th_to_75th_percentile_func(list_of_Ds)
    return robust_average_D


if __name__ == "__main__":
    # TODO: This was set by Jeff, do NOT change yet!
    TARGET_SIZE = (224, 224)

    # Test files:
    image_root = sys.argv[1]
    all_works = os.path.join(image_root, 'all_works')
    dupe_images = os.path.join(image_root, 'dupes')
    nondupe_images = os.path.join(image_root, 'nondupes')

    dupedetector = DupeDetector()

    # fingerprint_db = {get_sha256_hash_of_input_data_func(b"HASH")}
    fingerprint_db = populate_fingerprint_db(all_works, dupedetector, target_size=TARGET_SIZE)

    # assemble fingerprints
    pandas_table = assemble_fingerprints_for_pandas(fingerprint_db)

    print('\n\nNow testing duplicate-detection scheme on known near-duplicate images:\n')
    filelist = list_files(dupe_images)

    list_of_duplicate_check_results__near_dupes = list()
    list_of_duplicate_check_params__near_dupes = list()
    for current_near_dupe_file_path in filelist:
        print(
            '\n________________________________________________________________________________________________________________')
        print('\nCurrent Near Duplicate Image: ' + current_near_dupe_file_path)

        _, candidate_image_fingerprint = get_fingerprint_for_file(current_near_dupe_file_path, dupedetector, TARGET_SIZE)
        is_likely_dupe, params_df = measure_similarity(candidate_image_fingerprint, pandas_table)


        exit()


        print('\nParameters for current image:')
        print(params_df)
        list_of_duplicate_check_results__near_dupes.append(is_likely_dupe)
        list_of_duplicate_check_params__near_dupes.append(params_df)
    duplicate_detection_accuracy_percentage__near_dupes = sum(list_of_duplicate_check_results__near_dupes) / len(
        list_of_duplicate_check_results__near_dupes)
    print(
        '________________________________________________________________________________________________________________')
    print(
        '________________________________________________________________________________________________________________')
    print('\nAccuracy Percentage in Detecting Near-Duplicate Images: ' + str(
        round(100 * duplicate_detection_accuracy_percentage__near_dupes, 2)) + '%')
    print(
        '________________________________________________________________________________________________________________')
    print(
        '________________________________________________________________________________________________________________')
    exit()

    # print('\n\nNow testing duplicate-detection scheme on known non-duplicate images:\n')
    # list_of_file_paths_of_non_duplicate_test_images = glob.glob(nondupe_images + '*')
    # random_sample_size__non_dupes = 10
    # list_of_file_paths_of_non_duplicate_images_random_sample = [list_of_file_paths_of_non_duplicate_test_images[i] for i
    #                                                             in sorted(
    #         random.sample(range(len(list_of_file_paths_of_non_duplicate_test_images)), random_sample_size__non_dupes))]
    # list_of_duplicate_check_results__non_dupes = list()
    # list_of_duplicate_check_params__non_dupes = list()
    # for current_non_dupe_file_path in list_of_file_paths_of_non_duplicate_images_random_sample:
    #     print(
    #         '\n________________________________________________________________________________________________________________')
    #     print('\nCurrent Non-Duplicate Test Image: ' + current_non_dupe_file_path)
    #     is_likely_dupe, params_df = measure_similarity(current_non_dupe_file_path, fingerprint_db)
    #     print('\nParameters for current image:')
    #     print(params_df)
    #     list_of_duplicate_check_results__non_dupes.append(is_likely_dupe)
    #     list_of_duplicate_check_params__non_dupes.append(params_df)
    # duplicate_detection_accuracy_percentage__non_dupes = 1 - sum(list_of_duplicate_check_results__non_dupes) / len(
    #     list_of_duplicate_check_results__non_dupes)
    # print(
    #     '________________________________________________________________________________________________________________')
    # print(
    #     '________________________________________________________________________________________________________________')
    # print('\nAccuracy Percentage in Detecting Non-Duplicate Images: ' + str(
    #     round(100 * duplicate_detection_accuracy_percentage__non_dupes, 2)) + '%')
    # print(
    #     '________________________________________________________________________________________________________________')
    # print(
    #     '________________________________________________________________________________________________________________')
    #
    # if 0:
    #     predicted_y = [i * 1 for i in list_of_duplicate_check_results__near_dupes] + [i * 1 for i in
    #                                                                                   list_of_duplicate_check_results__non_dupes]
    #     actual_y = [1 for x in list_of_duplicate_check_results__near_dupes] + [1 for x in
    #                                                                            list_of_duplicate_check_results__non_dupes]
    #     precision, recall, thresholds = sklearn.metrics.precision_recall_curve(actual_y, predicted_y)
    #     auprc_metric = sklearn.metrics.auc(recall, precision)
    #     average_precision = sklearn.metrics.average_precision_score(actual_y, predicted_y)
    #     print(
    #         'Across all near-duplicate and non-duplicate test images, the Area Under the Precision-Recall Curve (AUPRC) is ' + str(
    #             round(auprc_metric, 3)))
