#!/usr/bin/env python3

import wellmap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

df = wellmap.load(
      'std_curve.toml',
      data_loader=pd.read_csv,
      merge_cols=True,
      path_guess='{0.stem}.csv',
)

x = df['dilution']
y = df['Cq']
m, b, r, p, err = linregress(np.log10(x), y)

x_fit = np.logspace(0, 5)
y_fit = np.polyval((m, b), np.log10(x_fit))

r2 = r**2
eff = 100 * (10**(1/m) - 1)
label = 'R²={:.5f}\neff={:.2f}%'.format(r2, eff)

plt.plot(x_fit, y_fit, '--', label=label)
plt.plot(x, y, '+')
plt.legend(loc='best')
plt.xscale('log')
plt.xlabel('dilution')
plt.ylabel('Cq')
plt.show()
