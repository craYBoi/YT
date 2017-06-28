import numpy as np
from random import randint


IMAGE_PATH = 'ytow/static/template/images.np'
LABEL_PATH = 'ytow/static/template/labels.np'
IMAGE_K_PATH = 'ytow/static/template/images_k.np'
LABEL_K_PATH = 'ytow/static/template/labels_k.np'

class MnistClassifier(object):
    def __init__(self, is_k=None):

        if is_k:
            self.train_images = np.load(IMAGE_K_PATH)
            self.train_labels = np.load(LABEL_K_PATH)
        else:
            self.train_images = np.load(IMAGE_PATH)
            self.train_labels = np.load(LABEL_PATH)

        # self.test_images = mnist_helper2.test_images
        # self.test_labels = mnist_helper2.test_labels

        self.IMAGE_LENGTH = 170
        self.NUM_OF_CLASSES = 11
        self.NUM_OF_BATHCES = 200
        self.BATCH_SIZE = 10
        self.LEARNING_RATE = 0.4

        self.W = np.random.random((170, 11))
        self.b = np.random.random((1, 11))

    # constructor override
    # def __init__(self, num_of_classes, image_length):
    #     self.__init__()
    #     self.IMAGE_LENGTH = image_length
    #     self.NUM_OF_CLASSES = num_of_classes
    #
    #     self.W = np.random.random((image_length, num_of_class))
    #     self.b = np.random.random((1, num_of_classes))


    #### Helper functions ####

    # softmax function
    # input -> logits (1, 10)
    # return -> probs (1, 10)
    def softmax(self, input_vec):
        exp_list = np.exp(input_vec - np.max(input_vec))
        return exp_list / np.sum(exp_list)


    # arg max function
    # input -> prediction probs (32, 10)
    # return -> one-hot arg max (32, 10)
    def arg_max(self, input_batch_predictions):
        width = input_batch_predictions.shape[0]
        arg_max_index = input_batch_predictions.argmax(axis=1)

        one_hot_batch_predictions = np.zeros(input_batch_predictions.shape)

        one_hot_batch_predictions[np.arange(width), arg_max_index] += 1

        # return one_hot_batch_predictions
        return arg_max_index



    # To one hot function
    # input -> batch of label (32, )
    # return -> batch of one-hot label (32, 10)
    def to_one_hot(self, label_batch):
        res_label = np.zeros((self.BATCH_SIZE, self.NUM_OF_CLASSES))

        res_label[np.arange(self.BATCH_SIZE), label_batch] += 1

        return res_label


    # Group images to batches, default n=32
    # return -> train_images (n, 784), train_labels (n, )
    def group_random_train_images(self, n=10):
        length = self.train_images.shape[0]
        batch_images = np.empty((n, self.IMAGE_LENGTH))
        batch_labels = np.empty((n, ), dtype=int)

        for i in range(n):
            random_num = randint(0, length-1)
            batch_images[i, :] = self.train_images[random_num, :]
            batch_labels[i] = self.train_labels[random_num]

        return (batch_images, batch_labels)


    #### Core Functions ####

    # forward pass function
    # input -> batch_images (32, 784)
    # return -> predictions of probs of labels (32, 10)
    def forward_pass(self, batch_images):
        logits = np.dot(batch_images, self.W) + self.b
        probs = np.apply_along_axis(self.softmax, 1, logits)

        return probs

    # back prop function that updates the weight/bias
    # input -> batch_images (32, 10)
    # prediction probs (32, 10)
    # truth_vec (32, )
    # return -> del_bias (32, 10), del_weight (784, 10)
    def back_propagate(self, batch_images, prediction_vec, truth_vec):
        truth_vec_one_hot = self.to_one_hot(truth_vec)

        del_b_batch = self.LEARNING_RATE * (np.negative(prediction_vec) + truth_vec_one_hot)
        # sum em up
        del_b = np.sum(del_b_batch, axis=0)

        del_X_l = prediction_vec - truth_vec_one_hot
        # no need to sum since np.dot already did the job
        del_W = np.negative(self.LEARNING_RATE * np.dot(batch_images.T, del_X_l))

        # update weight and bias
        self.W += del_W
        self.b += del_b


    # function train
    # run 10000 times, call forward pass and then back propagate
    # update weight and bias
    def train(self):

        # step a flag to detect if accuracy starts to drop

        for i in range(self.NUM_OF_BATHCES):
            batch_images, batch_labels = self.group_random_train_images()

            predictions = self.forward_pass(batch_images)

            self.back_propagate(batch_images, predictions, batch_labels)


    # test function
    # do forward pass on test images and compare to truth labels
    # return accuracy
    def test(self):
        predictions = self.forward_pass(self.test_images)

        # get the predictions
        prediction_labels = self.arg_max(predictions)

        # sum up the mask to get the number of hits
        hits = np.sum(prediction_labels == self.test_labels)

        return hits / float(prediction_labels.size)


    def predict(self, input_img):
        predictions = self.forward_pass(input_img)
        prediction_labels = self.arg_max(predictions)

        return prediction_labels
