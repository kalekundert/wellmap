#!/usr/bin/env python3

import wellmap

import pandas as pd
df = wellmap.load(
      'std_curve.toml',
      data_loader=pd.read_csv,
      merge_cols=True,
      path_guess='{0.stem}.csv',
)

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

x = df['dilution']
y = df['Cq']
m, b, r, p, err = linregress(np.log10(x), y)

x_fit = np.logspace(0, 5)
y_fit = np.polyval((m, b), np.log10(x_fit))

r2 = r**2
eff = 100 * (10**(1/m) - 1)

plt.plot(x_fit, y_fit, '--', label=f'R²={r2:.5f}\neff={eff:.2f}%')
plt.plot(x, y, '+')
plt.legend(loc='best')
plt.xscale('log')
plt.xlabel('dilution')
plt.ylabel('Cq')
plt.show()

# Reset margins to 10px after running this command.
#plt.savefig('std_curve_plot.svg')
