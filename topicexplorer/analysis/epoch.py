from functools import partial
from typing import Iterator, List, Sequence

import numpy as np
import numpy.ma as ma

def generate_epochs(N: int, dates: Sequence,
                    start: List[int]=None, limit: int=365) -> Iterator[List[int]]:
    if start is None:
        start = [0]

    if N <= 1:
        if (dates[start[-1]] <= (dates[-1] - limit)
           and start[-1] + 1 < len(dates)):
            e = start[:]
            e.append(len(dates))
            yield e[:]
    else:
        for i in range(start[-1]+2,len(dates)):
            if (dates[i] >= (dates[start[-1]] + limit)
                and dates[i] <= (dates[-1] - limit)):
                e = start[:]
                e.append(i)
                for epoch in generate_epochs(N-1, dates, e, limit=limit):
                    yield epoch[:]

def mean_mle(s):
    return np.sum(s) / len(s)

def variance_mle(s):
    return np.sum((s - mean_mle(s))**2) / len(s)

def mle(e, values):
    temp = []
    for i in range(len(e) - 1):
        s = values[e[i]:e[i+1]]

        val = len(s) / 2.
        val *= (1 + np.log(2*np.pi*variance_mle(s)))
        val *= -1
        temp.append(val)
    
    return np.sum(temp)

def aic(k, L):
    return 2*k - 2*L

def relative_mle(L, values):
    base = mle([0, len(values)], values)
    return np.exp((aic(2, base) - aic(8, L)) / 2)

def relative_joint_mle(L, t2t, p2t):
    base_t2t = mle([0, len(t2t)], t2t)
    base_p2t = mle([0, len(p2t)], p2t)
    return np.exp((aic(4, base_t2t+base_p2t) - aic(14, L))/2)

def get_all_data(epochs: List[int], t2t: Sequence, p2t: Sequence):
    data = [(e[1], e[2], mle(e, t2t) + mle(e, p2t)) for e in epochs]
    a = np.zeros(shape=(len(t2t), len(t2t)))
    for b,c,d in data:
        a[b,c] = d
    
    return ma.masked_equal(a, 0)

def indep_t2t(dates: Sequence, t2t: Sequence, num_epochs: int=2, years: int=5):
    return max(
        generate_epochs(num_epochs, dates, limit=365*years),
        key=partial(mle, values=t2t)
    )

def indep_p2t(dates: Sequence, p2t: Sequence, num_epochs: int=2, years: int=5):
    return max(
        generate_epochs(num_epochs, dates, limit=365*years),
        key=partial(mle, values=p2t)
    )

def joint(dates: Sequence, t2t: Sequence, p2t: Sequence, num_epochs: int=2, years: int=5):
    return max(
        generate_epochs(num_epochs, dates, limit=365*years), 
        key=lambda e: mle(e, t2t) + mle(e, p2t)
    )


#alldata= dict()
#alldata[0] = get_all_data(generate_epochs(3,limit=0))
#alldata[2] = get_all_data(generate_epochs(3,limit=2*365))
#alldata[5] = get_all_data(generate_epochs(3,limit=5*365))