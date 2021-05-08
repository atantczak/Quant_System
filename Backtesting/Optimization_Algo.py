import os

import numpy as np
import math

from Strategy_Analysis import RunAnalysis
from get_sp500_tickers import get_sp500


def run_optimization(ma_len):
    year = 2020
    tickers = os.listdir(
        '../../Data_Store/Russell_OHLCV_Data/{}/'.format(year))  # If you're pulling tickers for Russell
    tickers = [os.path.splitext(x)[0] for x in tickers]  # If you're pulling tickers for Russell

    ma_len = int(math.floor(ma_len))

    ra = RunAnalysis(tickers, 'Bollinger Bull', [year, '{}-04-01'.format(year), ma_len, 1])
    trades = ra.run_sim()

    exp_val = np.mean(trades)

    return exp_val


def diff_evolution(fobj, bounds, mut=0.8, crossp=0.7, popsize=20, its=1000):
    dimensions = len(bounds)
    pop = np.random.rand(popsize, dimensions)
    min_b, max_b = np.asarray(bounds).T
    diff = np.fabs(min_b - max_b)
    pop_denorm = min_b + pop * diff
    fitness = np.asarray([fobj(ind) for ind in pop_denorm])
    best_idx = np.argmin(fitness)
    best = pop_denorm[best_idx]
    for i in range(its):
        for j in range(popsize):
            idxs = [idx for idx in range(popsize) if idx != j]
            a, b, c = pop[np.random.choice(idxs, 3, replace = False)]
            mutant = np.clip(a + mut * (b - c), 0, 1)
            cross_points = np.random.rand(dimensions) < crossp
            if not np.any(cross_points):
                cross_points[np.random.randint(0, dimensions)] = True
            trial = np.where(cross_points, mutant, pop[j])
            trial_denorm = min_b + trial * diff
            f = fobj(trial_denorm)
            if f < fitness[j]:
                fitness[j] = f
                pop[j] = trial
                if f < fitness[best_idx]:
                    best_idx = j
                    best = trial_denorm
        yield best, fitness[best_idx]


def maximize(params):
    return -1*run_optimization(params[0])


result = list(diff_evolution(maximize, [(1, 30)], popsize=10, its=50))

print(result)