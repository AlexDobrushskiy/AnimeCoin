import os
import pickle
import sys
import hashlib

import keras
import pandas as pd

from dht_prototype.masternode_modules.animecoin_modules.animecoin_dupe_detection import DupeDetector, measure_similarity


def get_sha256_hash_of_input_data_func(input_data_or_string):
    if isinstance(input_data_or_string, str):
        input_data_or_string = input_data_or_string.encode('utf-8')
    sha256_hash_of_input_data = hashlib.sha3_256(input_data_or_string).hexdigest()
    return sha256_hash_of_input_data


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


def compute_fingerprint_for_single_image(filepath, dupedetector):
    imagehash, fingerprints = get_fingerprint_for_file(filepath, dupedetector, TARGET_SIZE)
    combined = combine_fingerprint_vectors(fingerprints)

    A = pd.DataFrame([imagehash, filepath]).T
    B = pd.DataFrame(combined)
    combined_image_fingerprint_df_row = pd.concat([A, B], axis=1, join_axes=[A.index])
    fingerprint = combined_image_fingerprint_df_row.iloc[:,2:].T.values.flatten().tolist()
    return fingerprint


def test_files_for_duplicates(dupe_images, pandas_table, dupedetector):
    filelist = list_files(dupe_images)

    ret = []
    for filename in filelist:
        print('Testing file: ' + filename)

        # compute fingerprint
        prepared_fingerprint = compute_fingerprint_for_single_image(filename, dupedetector)
        is_likely_dupe, params_df = measure_similarity(prepared_fingerprint, pandas_table)

        if is_likely_dupe:
            print("Art file (%s) appears to be a DUPLICATE!" % filename)
        else:
            print("Art file (%s) appears to be an ORIGINAL!" % filename)

        print('Parameters for current image:')
        print(params_df)
        ret.append(is_likely_dupe)

    accuracy = sum(ret) / len(ret)
    return accuracy


def main(target_size):
    # parse parameters
    image_root = sys.argv[1]
    database_filename = sys.argv[2]
    regenerate = False
    if len(sys.argv) > 3 and sys.argv[3] == "regenerate":
        regenerate = True

    # folder structure
    all_works = os.path.join(image_root, 'all_works')
    dupe_images = os.path.join(image_root, 'dupes')
    nondupe_images = os.path.join(image_root, 'nondupes')

    # initializing keras (might take long)
    dupedetector = DupeDetector()

    # do we need to regenerate the DB?
    if regenerate:
        print("Regenerate is True, generating fingerprint database")
        key = input("Would you like to overwrite %s (y/n): " % database_filename)
        if key == "y":
            with open(database_filename, "wb") as f:
                fingerprint_db = populate_fingerprint_db(all_works, dupedetector, target_size=target_size)
                f.write(pickle.dumps(fingerprint_db))
        print("Done")
        return
    else:
        print("Regenerate is False, loading from disk: %s" % database_filename)
        fingerprint_db = pickle.load(open(database_filename, "rb"))
        print("Loaded %s fingerprints" % len(fingerprint_db))

    # assemble fingerprints
    pandas_table = assemble_fingerprints_for_pandas([(k, v) for k, v in fingerprint_db.items()])

    # tests
    print('Now testing duplicate-detection scheme on known near-duplicate images')
    accuracy = test_files_for_duplicates(dupe_images, pandas_table, dupedetector)
    print('\nAccuracy Percentage in Detecting Near-Duplicate Images: ' + str(round(100 * accuracy, 2)) + '%')

    print('Now testing duplicate-detection scheme on known non-duplicate images')
    accuracy = test_files_for_duplicates(nondupe_images, pandas_table, dupedetector)
    print('\nAccuracy Percentage in Detecting Near-Duplicate Images: ' + str(round(100 * accuracy, 2)) + '%')


if __name__ == "__main__":
    # TODO: This was set by Jeff, do NOT change yet!
    TARGET_SIZE = (224, 224)
    main(TARGET_SIZE)
