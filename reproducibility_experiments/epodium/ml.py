# -*- coding: utf-8 -*-

import os

from glob import glob

import pandas as pd
import numpy as np

from joblib import dump, load
from scipy.stats import uniform
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, make_scorer
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVR, SVR
from sklearn.utils import shuffle
from sklearn_rvm import EMRVR


class Regression:

    def __init__(self, loader):
        self.loader = loader
        self.scaler = StandardScaler()
        self.rnd_search_defaults = {
            'n_iter': 100,
            'cv': 5,
            'n_jobs': 2,
            'scoring': self.scorer(),
            'verbose': 10,
        }
        self.gs_defaults = {
            'cv': 5,
            'n_jobs': -1,
            'scoring': self.scorer(),
            'verbose': 10,
        }

    def scorer(self):
        return make_scorer(mean_absolute_error, greater_is_better=False)

    def dump(self, result):
        fname = type(self).__name__.lower()
        if isinstance(result, GridSearchCV):
            fname += '-grid-search'
        elif isinstance(result, RandomizedSearchCV):
            fname += '-random-search'
        ofile = os.path.join(self.loader.models, fname)
        dump(result, f'{ofile}.joblib')
        return result

    def xy_train(self):
        return self.loader.x_train_val, self.loader.y_train_val

    def fit(self):
        pipeline = make_pipeline(self.scaler, self.kernel)
        result = RandomizedSearchCV(
            pipeline,
            self.parameters,
            **self.rnd_search_defaults
        )
        result.fit(*self.xy_train())
        return self.dump(result)

    def grid_search(self):
        if hasattr(self, 'gs_kernel'):
            kernel = self.gs_kernel
        else:
            kernel = self.kernel

        pipeline = make_pipeline(self.scaler, kernel)

        if hasattr(self, 'gs_parameters'):
            parameters = self.gs_parameters
        else:
            parameters = self.parameters

        result = GridSearchCV(pipeline, parameters, **self.gs_defaults)
        result.fit(*self.xy_train())
        return self.dump(result)

    def best_fit(self):
        result = make_pipeline(self.scaler, self.best_kernel)
        result.fit(*self.xy_train())
        return self.dump(result)


class Regressions:

    def __init__(self, loader):
        self.loader = loader
        self.algorithms = {
            'dummy': Dummy(self.loader),
            'rf': RandomForest(self.loader),
            'lsv': Lsv(self.loader),
            'sgd': Sgd(self.loader),
            'emrvr': Emrvr(self.loader),
            'svr': Svr(self.loader),
        }

    def algorithm(self, name):
        return self.algorithms[name]


class Dummy(Regression):

    def grid_search(self):
        raise NotImplemented

    def fit(self):
        dummy_regr = DummyRegressor(strategy="mean")
        dummy_regr.fit(*self.xy_train())
        return self.dump(dummy_regr)

    def best_fit(self):
        raise NotImplemented


class RandomForest(Regression):

    parameters = {
        'max_features': [
            'sqrt', 'log2', 15, 30, 40, 50, 60, 70, 80, 90, 100, 150, 250, None
        ],
        'min_samples_leaf': [1, 2, 3, 4, 5, 10, 20, 30, 40, 50]
    }

    def __init__(self, loader):
        super().__init__(loader)
        self.kernel = RandomForestRegressor(
            n_estimators=100,
            verbose=10,
            n_jobs=-1,
        )
        self.best_kernel = RandomForestRegressor(
            n_estimators=100,
            max_features=250,
            min_samples_leaf=10,
            n_jobs=-1,
        )

    def fit(self):
        # TODO(wvxvw): Figure out why is this so special: it doesn't
        # use randomized search and pipeline.
        self.kernel.fit(*self.xy_train())
        return self.dump(self.kernel)

    def grid_search(self):
        # TODO(wvxvw): Figure out why is this so special: it doesn't
        # use pipeline.
        gs = GridSearchCV(self.kernel, self.parameters, verbose=10, n_jobs=1)
        gs.fit(*self.xy_train())
        return self.dump(gs)


class Lsv(Regression):

    # Started with large parameter space, decreased the range of
    # parameters and increased training data RS with 1/10th of data
    # shows that C = 0.75 performs best and epsilon = 2.5
    parameters = {
        'linearsvr__C': uniform(0.01, 1),
        'linearsvr__epsilon': uniform(0, 6),
    }

    gs_parameters = {
        'linearsvr__C': [0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8],
        'linearsvr__epsilon': [1.5, 2, 2.5, 3],
    }

    def __init__(self, loader):
        super().__init__(loader)
        self.kernel = LinearSVR(verbose=2, max_iter=50000)
        self.best_kernel = LinearSVR(
            verbose=0,
            C=0.45,
            epsilon=2.5,
            max_iter=50000,
        )


class Svr(Regression):

    parameters = {
        'svr__C': uniform(0.01, 50),
        'svr__epsilon': uniform(0, 6),
        'svr__gamma': uniform(0.00001, 0.01)
    }

    gs_parameters = {
        'svr__C': [
            10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30,
            32.5, 35, 37.5, 40, 42.5, 45, 47.5, 50
        ],
        'svr__epsilon': [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5]
    }

    def __init__(self, loader):
        super().__init__(loader)
        self.kernel = SVR(verbose=True)
        self.gs_kernel = SVR(verbose=True, kernel='rbf')
        self.best_kernel = SVR(C=20, epsilon=1.5, kernel='rbf')


class Sgd(Regression):

    # Loss epsilon insensitive/huber are okay, squared loss/squared epsilon is really bad
    # Penalty doesn't really matter, l1 best, L1 ratio can therefore be ignored
    # Alpha 0.001-0.003
    # Epsilon 2.5-5.0
    parameters = {
        'sgdregressor__loss': ['huber', 'epsilon_insensitive'],
        'sgdregressor__alpha': uniform(0.001, 0.003),
        'sgdregressor__epsilon': uniform(2.5, 5),
    }

    gs_parameters = {
        'sgdregressor__loss': ['huber', 'epsilon_insensitive'],
        'sgdregressor__alpha': [0.0010, 0.0015, 0.0020, 0.0025, 0.0030],
        'sgdregressor__epsilon': [2.5, 3, 3.5, 4, 4.5, 5],
    }

    def __init__(self, loader):
        super().__init__(loader)
        self.kernel = SGDRegressor(verbose=10)
        self.best_kernel = SGDRegressor(
            alpha=0.001,
            epsilon=2.5,
            loss='epsilon_insensitive',
        )
        self.rnd_search_defaults['n_iter'] = 1000


class Emrvr(Regression):

    parameters = {
        'emrvr__kernel': ['poly', 'rbf', 'sigmoid'],
        'emrvr__degree': [3, 4, 5, 6, 7],
        'emrvr__epsilon': uniform(0, 6),
        'emrvr__gamma': uniform(0.00001, 0.01)
    }

    def __init__(self, loader):
        super().__init__(loader)
        self.kernel = EMRVR(verbose=True, max_iter=50000)
        self.best_kernel = EMRVR(kernel='rbf', epsilon=1.5, gamma=(1 / 450))
