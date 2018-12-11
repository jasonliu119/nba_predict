import numpy as np
import random

input_train = []
input_train_label = []

input_test = []
input_test_label = []

train_rate = 0.7

def is_train():
    return train_rate > random.random()

def read_input(input_file):
    lines = []
    with open(input_file, 'r') as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        label_count = 0
        is_train_data = is_train()
        x = []

        for j in range(4): # 4 dealers
            features = map(float, lines[i].strip().split())
            x.append(features)
            i = i + 1

            label_line = lines[i].strip()
            label_count = label_count + int(label_line)
            i = i + 1

        label = 1
        if label_count == 4:
            label = 1
        elif label_count == -4:
            label = 0
        if is_train_data:
            input_train.append(x)
            input_train_label.append(label)
        else:
            input_test.append(x)
            input_test_label.append(label)

# reading inputs
read_input('win_game_features-2017-2018.txt')
print "input_train len " + str(len(input_train))
print "input_train_label len " + str(len(input_train_label))
print "input_test len " + str(len(input_test))
print "input_test_label len " + str(len(input_test_label))

input_train_features = np.array(input_train)
input_train_label = np.array(input_train_label)

input_test_features = np.array(input_test)
input_test_label = np.array(input_test_label)

# training
import tensorflow as tf

# Specify feature
feature_columns = [tf.feature_column.numeric_column("x", shape=[4, 10])]

# Build 2 layer DNN classifier
classifier = tf.estimator.DNNClassifier(
    feature_columns=feature_columns,
    hidden_units=[20, 10],
    optimizer=tf.train.AdamOptimizer(1e-4),
    n_classes=2,
    activation_fn=tf.nn.relu
)

# Define the training inputs
train_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": input_train_features},
    y=input_train_label,
    num_epochs=None,
    batch_size=2,
    shuffle=True
)

classifier.train(input_fn=train_input_fn, steps=1000)

# Define the test inputs
test_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": input_test_features},
    y=input_test_label,
    num_epochs=1,
    shuffle=False
)

# Evaluate accuracy
accuracy_score = classifier.evaluate(input_fn=test_input_fn)["accuracy"]
print("\nTest Accuracy: {0:f}%\n".format(accuracy_score*100))