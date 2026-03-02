# OptiSample: Analytical Sample Size Estimator

## Overview
OptiSample is a graphical user interface (GUI) application designed for the precise determination of optimal sample sizes. The underlying algorithmic logic relies on the classical confidence interval approach for the mean of a normal continuous distribution. 

## Methodology
The application automates the calculation of the required sample size to achieve a specified margin of error, eliminating arbitrary or heuristic estimations. The implemented mathematical model is:

$$n = \left(\frac{Z \cdot \sigma}{E}\right)^2$$

Where:
* $n$ represents the minimum required sample size.
* $Z$ is the critical value (Z-score) derived from the standard normal distribution for the desired confidence level.
* $\sigma$ is the sample standard deviation computed from the preliminary raw data.
* $E$ is the predetermined maximum acceptable margin of error.

## References
The statistical foundation implemented in this software relies on established sampling theory standards:

* Cochran, W. G. (1977). *Sampling Techniques* (3rd ed.). John Wiley & Sons.
  * **Chapter 4:** The Estimation of Sample Size
  * **Section 4.6:** The formula for n with continuous data (p. 78)
  * **Methodological Note:** The algorithm directly implements Cochran's analytical derivation for absolute error control: $$n_0 = \frac{t^2 S^2}{d^2}$$. In the context of this application's variables, Cochran's $t$ corresponds to the normal deviate/Z-score ($Z$), $S$ corresponds to the sample standard deviation ($\sigma$), and $d$ corresponds to the target margin of error ($E$), resulting in the applied formula: $$n = \left(\frac{Z \cdot \sigma}{E}\right)^2$$.

## Installation and Execution
1. Clone this repository to your local machine.
2. Install the required dependencies: `pip install -r requirements.txt`
3. Execute the application: `python main.py`

## Data Input
The application accepts data via the system clipboard (as a single column of numerical values) or by importing standard `.csv` and `.xlsx` files.