import sys
import os

import tensorflow as tf


def check_image_file_nsfw_score_func(nsfw_model_file, image_file):
    with tf.gfile.FastGFile(nsfw_model_file, 'rb') as f:  # Unpersists graph from file
        nsfw_graph = tf.GraphDef()
        nsfw_graph.ParseFromString(f.read())

    tf.import_graph_def(nsfw_graph, name='')

    image_data = tf.gfile.FastGFile(image_file, 'rb').read()
    with tf.Session() as sess:
        # Feed the image_data as input to the graph and get first prediction
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
        predictions = sess.run(softmax_tensor,  {'DecodeJpeg/contents:0': image_data})

        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
        print(top_k)
        for graph_node_id in top_k:
            image_sfw_score = predictions[0][graph_node_id]
            print(image_sfw_score)
        image_nsfw_score = 1 - image_sfw_score

        return image_nsfw_score, nsfw_graph


def main(nsfw_model_file, image_file):
    check_image_file_nsfw_score_func(nsfw_model_file, image_file)


if __name__ == "__main__":
    nsfw_model_file = sys.argv[1]
    image_file = sys.argv[2]
    main(nsfw_model_file, image_file)
