"""
Module algorithm: Bayesian Gaussian Mixture Model
"""

import collections

import dask
import numpy as np
import sklearn.mixture


class Algorithm:

    def __init__(self, matrix: np.ndarray, parameters: collections.namedtuple):

        self.matrix = matrix
        self.parameters = parameters

    def modelling(self, n_components: int, covariance_type: str, n_init: int,
                  weight_concentration_prior_type: str):

        try:
            model = sklearn.mixture.BayesianGaussianMixture(
                n_components=n_components, covariance_type=covariance_type, tol=0.001, reg_covar=1e-06, max_iter=100,
                n_init=n_init, init_params='kmeans', weight_concentration_prior_type=weight_concentration_prior_type,
                weight_concentration_prior=None, mean_precision_prior=None, mean_prior=None,
                degrees_of_freedom_prior=None, covariance_prior=None, random_state=self.parameters.random_state,
                warm_start=False, verbose=0, verbose_interval=10
            ).fit(X=self.matrix)
        except OSError as _:
            print('Impossible ... K: {}, Covariance Type: {}'.format(n_components, covariance_type))
            model = None

        return model

    def exc(self):

        computations = [
            dask.delayed(self.modelling)(n_components, covariance_type, n_init, weight_concentration_prior_type)
            for n_components in self.parameters.array_n_components
            for covariance_type in self.parameters.array_covariance_type
            for n_init in self.parameters.array_n_init
            for weight_concentration_prior_type in self.parameters.array_weight_concentration_prior_type]

        models = dask.compute(computations, scheduler='processes')[0]
        models = [model for model in models if model is not None]

        return models
