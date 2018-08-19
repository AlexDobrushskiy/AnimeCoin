import os
import pickle
import sys
import hashlib
import time

from scipy.stats import rankdata
import keras
import numpy as np
import pandas as pd

from dht_prototype.masternode_modules.animecoin_modules.animecoin_dupe_detection import DupeDetector, measure_similarity


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


def list_files(basedir):
    files = []
    for i in sorted(os.listdir(basedir)):
        if i.split(".")[-1] in ["jpg", "jpeg", "bmp", "gif", "png"]:
            files.append(os.path.join(basedir, i))
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


def combine_fingerprint_vectors(fingerprint_collection):
    # concatenate fingerprints from various models and append it to rows
    combined = []
    for modelname, fingerprints in fingerprint_collection.items():
        fingerprint_vector = [x[0] for x in fingerprints]

        combined += fingerprint_vector
    return pd.DataFrame(combined).T


def assemble_fingerprints_for_pandas(db):
    df_vectors = pd.DataFrame()
    pandas_fingerprint_table = pd.DataFrame()

    for current_image_file_hash, data in db:
        file_path, fingerprint_collection = data

        combined = combine_fingerprint_vectors(fingerprint_collection)
        df_vectors = df_vectors.append(combined)

        # create dataframe rows for every image
        df_row = pd.DataFrame([current_image_file_hash, file_path]).T
        pandas_fingerprint_table = pandas_fingerprint_table.append(df_row)

    final_pandas_table = pd.concat([pandas_fingerprint_table, df_vectors], axis=1,
                                   join_axes=[pandas_fingerprint_table.index])
    return final_pandas_table


def populate_fingerprint_db(basedir, dupedetector, target_size):
    files = list_files(basedir)
    db = {}
    counter = 0
    for current_image_file_path in files:
        print('Now adding image file %s to image fingerprint database: %s/%s' % (current_image_file_path,
                                                                                 counter, len(files)))

        imghash, fingerprints = get_fingerprint_for_file(current_image_file_path, dupedetector, target_size)

        # add to the database
        db[imghash] = (current_image_file_path, fingerprints)
        counter += 1
    return db


# def calculate_randomized_dependence_coefficient_func(x, y, f=np.sin, k=20, s=1 / 6., n=1):
#     if n > 1:  # Note: Not actually using this because it gives errors constantly.
#         values = []
#         for i in range(n):
#             try:
#                 values.append(calculate_randomized_dependence_coefficient_func(x, y, f, k, s, 1))
#             except np.linalg.linalg.LinAlgError:
#                 pass
#         return np.median(values)
#     if len(x.shape) == 1: x = x.reshape((-1, 1))
#     if len(y.shape) == 1: y = y.reshape((-1, 1))
#     cx = np.column_stack([rankdata(xc, method='ordinal') for xc in x.T]) / float(x.size)  # Copula Transformation
#     cy = np.column_stack([rankdata(yc, method='ordinal') for yc in y.T]) / float(y.size)
#     O = np.ones(cx.shape[0])  # Add a vector of ones so that w.x + b is just a dot product
#     X = np.column_stack([cx, O])
#     Y = np.column_stack([cy, O])
#     Rx = (s / X.shape[1]) * np.random.randn(X.shape[1], k)  # Random linear projections
#     Ry = (s / Y.shape[1]) * np.random.randn(Y.shape[1], k)
#     X = np.dot(X, Rx)
#     Y = np.dot(Y, Ry)
#     fX = f(X)  # Apply non-linear function to random projections
#     fY = f(Y)
#     try:
#         C = np.cov(np.hstack([fX, fY]).T)  # Compute full covariance matrix
#         k0 = k
#         lb = 1
#         ub = k
#         while True:  # Compute canonical correlations
#             Cxx = C[:int(k), :int(k)]
#             Cyy = C[k0:k0 + int(k), k0:k0 + int(k)]
#             Cxy = C[:int(k), k0:k0 + int(k)]
#             Cyx = C[k0:k0 + int(k), :int(k)]
#             eigs = np.linalg.eigvals(np.dot(np.dot(np.linalg.inv(Cxx), Cxy), np.dot(np.linalg.inv(Cyy), Cyx)))
#             if not (np.all(np.isreal(eigs)) and  # Binary search if k is too large
#                     0 <= np.min(eigs) and
#                     np.max(eigs) <= 1):
#                 ub -= 1
#                 k = (ub + lb) / 2
#                 continue
#             if lb == ub: break
#             lb = k
#             if ub == lb + 1:
#                 k = ub
#             else:
#                 k = (ub + lb) / 2
#         return np.sqrt(np.max(eigs))
#     except:
#         return 0.0


def compute_fingerprint_for_single_image(filepath):
    imagehash, fingerprints = get_fingerprint_for_file(filepath, dupedetector, TARGET_SIZE)
    combined = combine_fingerprint_vectors(fingerprints)

    A = pd.DataFrame([imagehash, filepath]).T
    B = pd.DataFrame(combined)
    combined_image_fingerprint_df_row = pd.concat([A, B], axis=1, join_axes=[A.index])
    fingerprint = combined_image_fingerprint_df_row.iloc[:,2:].T.values.flatten().tolist()
    return fingerprint


if __name__ == "__main__":
    # TODO: This was set by Jeff, do NOT change yet!
    TARGET_SIZE = (224, 224)

    image_root = sys.argv[1]
    database_filename = sys.argv[2]
    regenerate = False
    if len(sys.argv) > 3 and sys.argv[3] == "regenerate":
        regenerate = True

    all_works = os.path.join(image_root, 'all_works')
    dupe_images = os.path.join(image_root, 'dupes')
    nondupe_images = os.path.join(image_root, 'nondupes')

    dupedetector = DupeDetector()

    if regenerate:
        print("Regenerate is True, generating fingerprint database")
        key = input("Would you like to overwrite %s (y/n): " % database_filename)
        if key == "y":
            with open(database_filename, "wb") as f:
                fingerprint_db = populate_fingerprint_db(all_works, dupedetector, target_size=TARGET_SIZE)
                f.write(pickle.dumps(fingerprint_db))
        print("Done")
        exit(0)
    else:
        print("Regenerate is False, loading from disk: %s" % database_filename)
        fingerprint_db = pickle.load(open(database_filename, "rb"))
        print("Loaded %s fingerprints" % len(fingerprint_db))

    # assemble fingerprints
    pandas_table = assemble_fingerprints_for_pandas([(k,v) for k, v in fingerprint_db.items()])

    print('\n\nNow testing duplicate-detection scheme on known near-duplicate images:\n')
    filelist = list_files(dupe_images)

    list_of_duplicate_check_results__near_dupes = list()
    list_of_duplicate_check_params__near_dupes = list()
    for current_near_dupe_file_path in filelist:
        print(
            '\n________________________________________________________________________________________________________________')
        print('\nCurrent Near Duplicate Image: ' + current_near_dupe_file_path)

        # compute fingerprint
        candidate_image_fingerprint_transposed_values = compute_fingerprint_for_single_image(current_near_dupe_file_path)
        is_likely_dupe, params_df = measure_similarity(candidate_image_fingerprint_transposed_values, pandas_table)

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


    print('\n\nNow testing duplicate-detection scheme on known non-duplicate images:\n')
    filelist = list_files(nondupe_images)

    list_of_duplicate_check_results__non_dupes = list()
    list_of_duplicate_check_params__non_dupes = list()
    for current_non_dupe_file_path in filelist:
        print(
            '\n________________________________________________________________________________________________________________')
        print('\nCurrent Non-Duplicate Test Image: ' + current_non_dupe_file_path)
        candidate_image_fingerprint_transposed_values = compute_fingerprint_for_single_image(
            current_non_dupe_file_path)
        is_likely_dupe, params_df = measure_similarity(candidate_image_fingerprint_transposed_values, pandas_table)
        print('\nParameters for current image:')
        print(params_df)
        list_of_duplicate_check_results__non_dupes.append(is_likely_dupe)
        list_of_duplicate_check_params__non_dupes.append(params_df)
    duplicate_detection_accuracy_percentage__non_dupes = 1 - sum(list_of_duplicate_check_results__non_dupes) / len(
        list_of_duplicate_check_results__non_dupes)
    print(
        '________________________________________________________________________________________________________________')
    print(
        '________________________________________________________________________________________________________________')
    print('\nAccuracy Percentage in Detecting Non-Duplicate Images: ' + str(
        round(100 * duplicate_detection_accuracy_percentage__non_dupes, 2)) + '%')
    print(
        '________________________________________________________________________________________________________________')
    print(
        '________________________________________________________________________________________________________________')
