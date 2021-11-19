import numpy as np

from .regressors import logistic
from .tools import get_train_test_split, calculate_accuracy, calculate_cost_mse

def get_bootstrap_sample(data):

    bootstrap_indices = np.random.choice(len(data['targets']) - 1, len(data['targets']))
    bootstrap_sample_data = { 'inputs': [item[bootstrap_indices] for item in data['inputs']], 'targets': data['targets'][bootstrap_indices] }

    return bootstrap_sample_data

def bootstrap(data, regressor, regressor_parameters, n_pol, n_samples, train_ratio=0.8):

    # lists to store output
    train_losses = []
    test_losses = []

    for i in range(n_samples):

        # partion into train and test set
        train_data, test_data = get_train_test_split(data, train_ratio=train_ratio)

        # get a bootstrap sample
        bootstrap_sample_data_train = get_bootstrap_sample(train_data)

        # perform regression and append to output variables
        train_prediction, test_prediction = regressor(regressor_parameters, bootstrap_sample_data_train, test_data, n_pol)
        
        if regressor == logistic:
            train_losses.append(calculate_accuracy(np.array(train_prediction > 0.5, dtype='int64'), bootstrap_sample_data_train['targets']))
            test_losses.append(calculate_accuracy(np.array(test_prediction > 0.5, dtype='int64'), test_data['targets']))
        else:
            train_losses.append(calculate_cost_mse(train_prediction, bootstrap_sample_data_train['targets']))
            test_losses.append(calculate_cost_mse(test_prediction, test_data['targets']))

    return train_losses, test_losses

def cross_validation(data, regressor, regressor_parameters, n_pol, n_folds):

    # get fold length
    fold_length = int(np.ceil(len(data['targets']) / n_folds))

    # lists to store output
    train_losses = []
    test_losses = []

    for i in range(n_folds):
        
        # get indices of validation data points for this fold
        start = i * fold_length
        stop = min([(i + 1) * fold_length, len(data['targets']) - 1])
        test_indices = list(range(start, stop, 1))

        # assign train and test data for this fold
        test_data = { 'inputs': [item[test_indices] for item in data['inputs']], 'targets': data['targets'][test_indices] }
        train_data = { 'inputs': [np.delete(item, test_indices) for item in data['inputs']], 'targets': np.delete(data['targets'], test_indices) }

        # perform regression and append to output variables
        train_prediction, test_prediction = regressor(regressor_parameters, train_data, test_data, n_pol)
        
        if regressor == logistic:
            train_losses.append(calculate_accuracy(np.array(train_prediction > 0.5, dtype='int64'), train_data['targets']))
            test_losses.append(calculate_accuracy(np.array(test_prediction > 0.5, dtype='int64'), test_data['targets']))
        else:
            train_losses.append(calculate_cost_mse(train_prediction, train_data['targets']))
            test_losses.append(calculate_cost_mse(test_prediction, test_data['targets']))

    return train_losses, test_losses
