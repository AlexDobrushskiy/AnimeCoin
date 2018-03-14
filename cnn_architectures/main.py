from data_loader import load_data, split_data, downsample_data, get_augmented_data, load_cifar_data
from vgg16 import vgg16_model
from SimNet import simnet_model
from keras.layers import Input
import numpy as np

if __name__ == '__main__':

    num_classes = 10
    batch_size = 16
    nb_epoch = 10
    from sklearn.metrics import log_loss
    X, y = load_data('CIFAR10')
    # from PIL import Image
    # Image.fromarray(X[220], 'RGB').show()

    def test_vgg():
        X_train, X_valid, Y_train, Y_valid = split_data(X, y)
        img_rows, img_cols, channels = X_train[0, :, :, :].shape

        model = vgg16_model(img_rows, img_cols, channels, num_classes)

        model.fit(X_train, Y_train,
                  batch_size=batch_size,
                  epochs=nb_epoch,
                  shuffle=True,
                  verbose=1,
                  validation_data=(X_valid, Y_valid),
                  )

        predictions_valid = model.predict(X_valid, batch_size=batch_size, verbose=1)

        score = log_loss(Y_valid, predictions_valid)
        print(score)

    def test_simnet_on_cifar():

        clusters = load_cifar_data()
        n_clusters = len(clusters)
        datasets = []

        for i in range(n_clusters):
            # make augmented data
            x = np.asarray(clusters[i])
            n_samples = len(x)
            y = np.zeros(n_samples) + i

            x_aug, _ = get_augmented_data(x, y, n_samples)
            x4, x8 = downsample_data(x)
            x_aug4, x_aug8 = downsample_data(x_aug)

            datasets.append([x, x4, x8, x_aug, x_aug4, x_aug8])

            mdl = simnet_model(x[0,:,:,0].shape,
                               x4[0, :, :, 0].shape,
                               x8[0, :, :, 0].shape,
                               3, 10)

            # model requires 1 normal img, 2 downsampled + label (1 if similar, 0 if dissimilar)
            # train on similar
            mdl.fit(
                {'img1' : x, 'img1_sc1' : x4, 'img1_sc2' : x8,
                'img2' : x_aug, 'img2_sc1' : x_aug4, 'img2_sc2' : x_aug8},
                {'distance' : np.zeros(n_samples)},
                epochs=10,
                batch_size=100,
                validation_split=0.33
            )

        # train on different
        for i in range(n_clusters):
            cluster_a = datasets[i]
            for j in range(i, n_clusters):
                size = np.abs(len(cluster_b)-len(cluster_a))
                cluster_a = cluster_a[:size]
                cluster_b = datasets[j][:size]
                mdl.fit(
                    {'img1': cluster_a[0], 'img1_sc1': cluster_a[1], 'img1_sc2': cluster_a[2],
                     'img2': cluster_b[0], 'img2_sc1': cluster_b[1], 'img2_sc2': cluster_b[2]},
                    {'distance': np.zeros(size)},
                    epochs=10,
                    batch_size=100,
                    validation_split=0.33
                )

    test_simnet_on_cifar()