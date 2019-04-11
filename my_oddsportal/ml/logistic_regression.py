from __future__ import print_function

import math
import os
from IPython import display
from matplotlib import cm
from matplotlib import gridspec
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics
import tensorflow as tf
from tensorflow.python.data import Dataset

tf.logging.set_verbosity(tf.logging.ERROR)
# pd.options.display.max_rows = 10
pd.options.display.float_format = '{:.5f}'.format
pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', -1)  # or 199

game_dataframe = pd.read_csv("./game_features-2017-2018.csv")
game_dataframe = game_dataframe.reindex(np.random.permutation(game_dataframe.index))

# Step 1: preprocess the features
def preprocess_features(game_dataframe):
  selected_features = game_dataframe[[
    'home_team_per_game_got_score',
    'home_team_per_game_lost_score',
    'home_team_per_home_game_got_score',
    'home_team_per_home_game_lost_score',
    'home_team_last_win_number_of_the_last_10_game',
    'home_team_rest_time_in_days',
    'home_team_ranking_of_all_the_teams',
    'home_team_home_win_rate',
    'home_team_win_rate',
    'away_team_per_game_got_score',
    'away_team_per_game_lost_score',
    'away_team_per_away_game_got_score',
    'away_team_per_away_game_lost_score',
    'away_team_last_win_number_of_the_last_10_game',
    'away_team_rest_time_in_days',
    'away_team_ranking_of_all_the_teams',
    'away_team_away_win_rate',
    'away_team_win_rate']]
  processed_features = selected_features.copy()
  return processed_features

def preprocess_targets(game_dataframe):
  output_targets = pd.DataFrame()
  output_targets["home_win_or_lose"] = (game_dataframe["home_win_or_lose"] == 1).astype(float)
  return output_targets

# Choose the first 800 (out of 1000) examples for training.
training_examples = preprocess_features(game_dataframe.head(900))
training_targets = preprocess_targets(game_dataframe.head(900))

# Choose the last 200 (out of 1000) examples for validation.
validation_examples = preprocess_features(game_dataframe.tail(100))
validation_targets = preprocess_targets(game_dataframe.tail(100))

# Double-check that we've done the right thing.
def display_stats():
    print("Training examples summary:")
    display.display(training_examples.describe(include = 'all'))
    print("Validation examples summary:")
    display.display(validation_examples.describe(include = 'all'))

    print("Training targets summary:")
    display.display(training_targets.describe(include = 'all'))
    print("Validation targets summary:")
    display.display(validation_targets.describe(include = 'all'))

def construct_feature_columns(input_features):
  """Construct the TensorFlow Feature Columns.

  Args:
    input_features: The names of the numerical input features to use.
  Returns:
    A set of feature columns
  """
  return set([tf.feature_column.numeric_column(my_feature)
              for my_feature in input_features])

def my_input_fn(features, targets, batch_size=1, shuffle=True, num_epochs=None):
    """Trains a linear regression model.
  
    Args:
      features: pandas DataFrame of features
      targets: pandas DataFrame of targets
      batch_size: Size of batches to be passed to the model
      shuffle: True or False. Whether to shuffle the data.
      num_epochs: Number of epochs for which data should be repeated. None = repeat indefinitely
    Returns:
      Tuple of (features, labels) for next data batch
    """
    
    # Convert pandas data into a dict of np arrays.
    features = {key:np.array(value) for key,value in dict(features).items()}                                            
 
    # Construct a dataset, and configure batching/repeating.
    ds = Dataset.from_tensor_slices((features,targets)) # warning: 2GB limit
    ds = ds.batch(batch_size).repeat(num_epochs)
    
    # Shuffle the data, if specified.
    if shuffle:
      ds = ds.shuffle(10000)
    
    # Return the next batch of data.
    features, labels = ds.make_one_shot_iterator().get_next()
    return features, labels

def train_linear_regressor_model(
    label_name,
    learning_rate,
    steps,
    batch_size,
    training_examples,
    training_targets,
    validation_examples,
    validation_targets):
  """Trains a linear regression model.
  
  In addition to training, this function also prints training progress information,
  as well as a plot of the training and validation loss over time.
  
  Args:
    learning_rate: A `float`, the learning rate.
    steps: A non-zero `int`, the total number of training steps. A training step
      consists of a forward and backward pass using a single batch.
    batch_size: A non-zero `int`, the batch size.
    training_examples: A `DataFrame` containing one or more columns from
      `california_housing_dataframe` to use as input features for training.
    training_targets: A `DataFrame` containing exactly one column from
      `california_housing_dataframe` to use as target for training.
    validation_examples: A `DataFrame` containing one or more columns from
      `california_housing_dataframe` to use as input features for validation.
    validation_targets: A `DataFrame` containing exactly one column from
      `california_housing_dataframe` to use as target for validation.
      
  Returns:
    A `LinearRegressor` object trained on the training data.
  """

  periods = 10
  steps_per_period = steps / periods

  # Create a linear regressor object.
  my_optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
  my_optimizer = tf.contrib.estimator.clip_gradients_by_norm(my_optimizer, 5.0)
  linear_regressor = tf.estimator.LinearRegressor(
      feature_columns=construct_feature_columns(training_examples),
      optimizer=my_optimizer
  )
    
  # Create input functions.
  training_input_fn = lambda: my_input_fn(training_examples, 
                                          training_targets[label_name], 
                                          batch_size=batch_size)
  predict_training_input_fn = lambda: my_input_fn(training_examples, 
                                                  training_targets[label_name], 
                                                  num_epochs=1, 
                                                  shuffle=False)
  predict_validation_input_fn = lambda: my_input_fn(validation_examples, 
                                                    validation_targets[label_name], 
                                                    num_epochs=1, 
                                                    shuffle=False)

  # Train the model, but do so inside a loop so that we can periodically assess
  # loss metrics.
  print("Training model...")
  print("RMSE (on training data):")
  training_rmse = []
  validation_rmse = []
  for period in range (0, periods):
    # Train the model, starting from the prior state.
    linear_regressor.train(
        input_fn=training_input_fn,
        steps=steps_per_period
    )
    
    # Take a break and compute predictions.
    training_predictions = linear_regressor.predict(input_fn=predict_training_input_fn)
    training_predictions = np.array([item['predictions'][0] for item in training_predictions])
    
    validation_predictions = linear_regressor.predict(input_fn=predict_validation_input_fn)
    validation_predictions = np.array([item['predictions'][0] for item in validation_predictions])
    
    # Compute training and validation loss.
    training_root_mean_squared_error = math.sqrt(
        metrics.mean_squared_error(training_predictions, training_targets))
    validation_root_mean_squared_error = math.sqrt(
        metrics.mean_squared_error(validation_predictions, validation_targets))
    # Occasionally print the current loss.
    print("  period %02d : %0.4f" % (period, training_root_mean_squared_error))
    # Add the loss metrics from this period to our list.
    training_rmse.append(training_root_mean_squared_error)
    validation_rmse.append(validation_root_mean_squared_error)
  print("Model training finished.")
  
  # Output a graph of loss metrics over periods.
  plt.ylabel("RMSE")
  plt.xlabel("Periods")
  plt.title("Root Mean Squared Error vs. Periods")
  plt.tight_layout()
  plt.plot(training_rmse, label="training")
  plt.plot(validation_rmse, label="validation")
  plt.legend()

  return linear_regressor

def train_linear_classifier_model(
    label_name,
    learning_rate,
    steps,
    batch_size,
    training_examples,
    training_targets,
    validation_examples,
    validation_targets):
  """Trains a linear classification model.
  
  In addition to training, this function also prints training progress information,
  as well as a plot of the training and validation loss over time.
  
  Args:
    learning_rate: A `float`, the learning rate.
    steps: A non-zero `int`, the total number of training steps. A training step
      consists of a forward and backward pass using a single batch.
    batch_size: A non-zero `int`, the batch size.
    training_examples: A `DataFrame` containing one or more columns from
      `california_housing_dataframe` to use as input features for training.
    training_targets: A `DataFrame` containing exactly one column from
      `california_housing_dataframe` to use as target for training.
    validation_examples: A `DataFrame` containing one or more columns from
      `california_housing_dataframe` to use as input features for validation.
    validation_targets: A `DataFrame` containing exactly one column from
      `california_housing_dataframe` to use as target for validation.
      
  Returns:
    A `LinearClassifier` object trained on the training data.
  """

  periods = 10
  steps_per_period = steps / periods
  
  # Create a linear classifier object.
  my_optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
  my_optimizer = tf.contrib.estimator.clip_gradients_by_norm(my_optimizer, 5.0)  
  linear_classifier = tf.estimator.LinearClassifier(
      feature_columns=construct_feature_columns(training_examples),
      optimizer=my_optimizer
  )
  
  # Create input functions.
  training_input_fn = lambda: my_input_fn(training_examples, 
                                          training_targets[label_name], 
                                          batch_size=batch_size)
  predict_training_input_fn = lambda: my_input_fn(training_examples, 
                                                  training_targets[label_name], 
                                                  num_epochs=1, 
                                                  shuffle=False)
  predict_validation_input_fn = lambda: my_input_fn(validation_examples, 
                                                    validation_targets[label_name], 
                                                    num_epochs=1, 
                                                    shuffle=False)
  
  # Train the model, but do so inside a loop so that we can periodically assess
  # loss metrics.
  print("Training model...")
  print("LogLoss (on training data):")
  training_log_losses = []
  validation_log_losses = []
  for period in range (0, periods):
    # Train the model, starting from the prior state.
    linear_classifier.train(
        input_fn=training_input_fn,
        steps=steps_per_period
    )
    # Take a break and compute predictions.    
    training_probabilities = linear_classifier.predict(input_fn=predict_training_input_fn)
    training_probabilities = np.array([item['probabilities'] for item in training_probabilities])
    
    validation_probabilities = linear_classifier.predict(input_fn=predict_validation_input_fn)
    validation_probabilities = np.array([item['probabilities'] for item in validation_probabilities])
    
    training_log_loss = metrics.log_loss(training_targets, training_probabilities)
    validation_log_loss = metrics.log_loss(validation_targets, validation_probabilities)
    # Occasionally print the current loss.
    print("  period %02d : %0.2f" % (period, training_log_loss))
    # Add the loss metrics from this period to our list.
    training_log_losses.append(training_log_loss)
    validation_log_losses.append(validation_log_loss)
  print("Model training finished.")
  
  # Output a graph of loss metrics over periods.
  plt.ylabel("LogLoss")
  plt.xlabel("Periods")
  plt.title("LogLoss vs. Periods")
  plt.tight_layout()
  plt.plot(training_log_losses, label="training")
  plt.plot(validation_log_losses, label="validation")
  plt.legend()

  return linear_classifier

# linear_regressor = train_linear_regressor_model(
#     label_name="home_win_or_lose",
#     learning_rate=0.00001,
#     steps=5000,
#     batch_size=50,
#     training_examples=training_examples,
#     training_targets=training_targets,
#     validation_examples=validation_examples,
#     validation_targets=validation_targets)

def run_linear_classifier():
    linear_classifier = train_linear_classifier_model(
        label_name="home_win_or_lose",
        learning_rate=0.00005,
        steps=5000,
        batch_size=50,
        training_examples=training_examples,
        training_targets=training_targets,
        validation_examples=validation_examples,
        validation_targets=validation_targets)

    predict_validation_input_fn = lambda: my_input_fn(validation_examples, 
                                                    validation_targets["home_win_or_lose"], 
                                                    num_epochs=1, 
                                                    shuffle=False)
    evaluation_metrics = linear_classifier.evaluate(input_fn=predict_validation_input_fn)
    for key in evaluation_metrics:
        print(key + " on the validation set: %0.3f" % evaluation_metrics[key])

'''
  period 00 : 0.67
  period 01 : 0.65
  period 02 : 0.65
  period 03 : 0.65
  period 04 : 0.64
  period 05 : 0.65
  period 06 : 0.64
  period 07 : 0.64
  period 08 : 0.64
  period 09 : 0.64
Model training finished.
AUC on the validation set: 0.72
Accuracy on the validation set: 0.74

  period 00 : 0.66
  period 01 : 0.64
  period 02 : 0.64
  period 03 : 0.64
  period 04 : 0.64
  period 05 : 0.63
  period 06 : 0.63
  period 07 : 0.63
  period 08 : 0.63
  period 09 : 0.63
Model training finished.
loss on the validation set: 0.621
accuracy_baseline on the validation set: 0.560
global_step on the validation set: 2000.000
recall on the validation set: 0.821
auc on the validation set: 0.715
prediction/mean on the validation set: 0.570
precision on the validation set: 0.687
label/mean on the validation set: 0.560
average_loss on the validation set: 0.621
auc_precision_recall on the validation set: 0.778
accuracy on the validation set: 0.690
'''

def train_nn_classification_model(
    label_name,
    learning_rate,
    steps,
    batch_size,
    hidden_units,
    training_examples,
    training_targets,
    validation_examples,
    validation_targets):
  """Trains a neural network classification model for the MNIST digits dataset.
  
  In addition to training, this function also prints training progress information,
  a plot of the training and validation loss over time, as well as a confusion
  matrix.
  
  Args:
    learning_rate: A `float`, the learning rate to use.
    steps: A non-zero `int`, the total number of training steps. A training step
      consists of a forward and backward pass using a single batch.
    batch_size: A non-zero `int`, the batch size.
    hidden_units: A `list` of int values, specifying the number of neurons in each layer.
    training_examples: A `DataFrame` containing the training features.
    training_targets: A `DataFrame` containing the training labels.
    validation_examples: A `DataFrame` containing the validation features.
    validation_targets: A `DataFrame` containing the validation labels.
      
  Returns:
    The trained `DNNClassifier` object.
  """

  periods = 10
  # Caution: input pipelines are reset with each call to train. 
  # If the number of steps is small, your model may never see most of the data.  
  # So with multiple `.train` calls like this you may want to control the length 
  # of training with num_epochs passed to the input_fn. Or, you can do a really-big shuffle, 
  # or since it's in-memory data, shuffle all the data in the `input_fn`.
  steps_per_period = steps / periods

  # Create input functions.
  training_input_fn = lambda: my_input_fn(training_examples, 
                                          training_targets[label_name], 
                                          batch_size=batch_size)
  predict_training_input_fn = lambda: my_input_fn(training_examples, 
                                                  training_targets[label_name], 
                                                  num_epochs=1, 
                                                  shuffle=False)
  predict_validation_input_fn = lambda: my_input_fn(validation_examples, 
                                                    validation_targets[label_name], 
                                                    num_epochs=1, 
                                                    shuffle=False)
  
  # Create a DNNClassifier object.
  my_optimizer = tf.train.AdagradOptimizer(learning_rate=learning_rate)
  my_optimizer = tf.contrib.estimator.clip_gradients_by_norm(my_optimizer, 1.0)
  classifier = tf.estimator.DNNClassifier(
      feature_columns=construct_feature_columns(training_examples),
      n_classes=2,
      hidden_units=hidden_units,
      optimizer=my_optimizer,
      config=tf.contrib.learn.RunConfig(keep_checkpoint_max=1)
  )

  # Train the model, but do so inside a loop so that we can periodically assess
  # loss metrics.
  print("Training model...")
  print("LogLoss error (on validation data):")
  training_errors = []
  validation_errors = []
  for period in range (0, periods):
    # Train the model, starting from the prior state.
    classifier.train(
        input_fn=training_input_fn,
        steps=steps_per_period
    )
  
    # Take a break and compute probabilities.
    training_predictions = list(classifier.predict(input_fn=predict_training_input_fn))
    training_probabilities = np.array([item['probabilities'] for item in training_predictions])
    training_pred_class_id = np.array([item['class_ids'][0] for item in training_predictions])
    training_pred_one_hot = tf.keras.utils.to_categorical(training_pred_class_id, 2)
        
    validation_predictions = list(classifier.predict(input_fn=predict_validation_input_fn))
    validation_probabilities = np.array([item['probabilities'] for item in validation_predictions])    
    validation_pred_class_id = np.array([item['class_ids'][0] for item in validation_predictions])
    validation_pred_one_hot = tf.keras.utils.to_categorical(validation_pred_class_id, 2)    
    
    # Compute training and validation errors.
    training_log_loss = metrics.log_loss(training_targets, training_pred_one_hot)
    validation_log_loss = metrics.log_loss(validation_targets, validation_pred_one_hot)
    # Occasionally print the current loss.
    print("  period %02d : %0.2f" % (period, validation_log_loss))
    # Add the loss metrics from this period to our list.
    training_errors.append(training_log_loss)
    validation_errors.append(validation_log_loss)
  print("Model training finished.")
  # Remove event files to save disk space.
  # _ = map(os.remove, glob.glob(os.path.join(classifier.model_dir, 'events.out.tfevents*')))
  
  # Calculate final predictions (not probabilities, as above).
  final_predictions = classifier.predict(input_fn=predict_validation_input_fn)
  final_predictions = np.array([item['class_ids'][0] for item in final_predictions])
  
  
  accuracy = metrics.accuracy_score(validation_targets, final_predictions)
  print("Final accuracy (on validation data): %0.2f" % accuracy)

  # Output a graph of loss metrics over periods.
  plt.ylabel("LogLoss")
  plt.xlabel("Periods")
  plt.title("LogLoss vs. Periods")
  plt.plot(training_errors, label="training")
  plt.plot(validation_errors, label="validation")
  plt.legend()
  plt.show()
  
  # # Output a plot of the confusion matrix.
  # cm = metrics.confusion_matrix(validation_targets, final_predictions)
  # # Normalize the confusion matrix by row (i.e by the number of samples
  # # in each class).
  # cm_normalized = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
  # ax = sns.heatmap(cm_normalized, cmap="bone_r")
  # ax.set_aspect(1)
  # plt.title("Confusion matrix")
  # plt.ylabel("True label")
  # plt.xlabel("Predicted label")
  # plt.show()

  return classifier

def run_nn_classifier():
    classifier = train_nn_classification_model(
        label_name="home_win_or_lose",
        learning_rate=0.0001,
        steps=2000,
        batch_size=50,
        hidden_units=[100, 100, 100],
        training_examples=training_examples,
        training_targets=training_targets,
        validation_examples=validation_examples,
        validation_targets=validation_targets)

    predict_validation_input_fn = lambda: my_input_fn(validation_examples, 
                                                    validation_targets["home_win_or_lose"], 
                                                    num_epochs=1, 
                                                    shuffle=False)
    evaluation_metrics = classifier.evaluate(input_fn=predict_validation_input_fn)
    for key in evaluation_metrics:
        print(key + " on the validation set: %0.3f" % evaluation_metrics[key])

if __name__ == "__main__":
    run_nn_classifier()

'''
Training model...
LogLoss error (on validation data):
2019-04-10 22:55:04.911530: I tensorflow/core/platform/cpu_feature_guard.cc:141] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2 FMA
  period 00 : 10.02
  period 01 : 8.98
  period 02 : 10.36
  period 03 : 9.67
  period 04 : 10.36
  period 05 : 10.36
  period 06 : 10.36
  period 07 : 9.67
  period 08 : 10.71
  period 09 : 10.36
Model training finished.
Final accuracy (on validation data): 0.70
loss on the validation set: 0.580
accuracy_baseline on the validation set: 0.600
global_step on the validation set: 2000.000
recall on the validation set: 0.817
auc on the validation set: 0.762
prediction/mean on the validation set: 0.607
precision on the validation set: 0.721
label/mean on the validation set: 0.600
average_loss on the validation set: 0.580
auc_precision_recall on the validation set: 0.818
accuracy on the validation set: 0.700
'''