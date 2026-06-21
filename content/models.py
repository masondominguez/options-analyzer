import numpy as np
from scipy.stats import norm


def black_scholes(S, K, T, r, sigma, option_type="call", q=0.0):
    """Calculate Black-Scholes European option price, Greeks, and ITM probability.
    
    q: continuous dividend yield (e.g. 0.015 for 1.5%). Defaults to 0 (no dividend).
    """
    if T <= 0 or sigma <= 0: return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    disc_q = np.exp(-q * T)
    disc_r = np.exp(-r * T)
    if option_type == "call":
        price = S * disc_q * norm.cdf(d1) - K * disc_r * norm.cdf(d2)
        delta = disc_q * norm.cdf(d1)
        theta = (- (S * disc_q * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
                 - r * K * disc_r * norm.cdf(d2)
                 + q * S * disc_q * norm.cdf(d1)) / 365
        prob_itm = norm.cdf(d2)
    else:
        price = K * disc_r * norm.cdf(-d2) - S * disc_q * norm.cdf(-d1)
        delta = disc_q * (norm.cdf(d1) - 1)
        theta = (- (S * disc_q * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
                 + r * K * disc_r * norm.cdf(-d2)
                 - q * S * disc_q * norm.cdf(-d1)) / 365
        prob_itm = norm.cdf(-d2)
    gamma = disc_q * norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = (S * disc_q * norm.pdf(d1) * np.sqrt(T)) / 100
    return price, delta, gamma, theta, vega, prob_itm


def binomial_tree_american(S, K, T, r, sigma, steps=100, option_type="call", q=0.0):
    """Calculate American option price using a CRR Binomial Tree.
    
    q: continuous dividend yield. Defaults to 0 (no dividend).
    """
    if T <= 0 or sigma <= 0: return 0.0
    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp((r - q) * dt) - d) / (u - d)
    asset_prices = np.array([S * (u ** j) * (d ** (steps - j)) for j in range(steps + 1)])
    if option_type == "call":
        option_values = np.maximum(0, asset_prices - K)
    else:
        option_values = np.maximum(0, K - asset_prices)
    for i in range(steps - 1, -1, -1):
        option_values = np.exp(-r * dt) * (p * option_values[1:i+2] + (1 - p) * option_values[0:i+1])
        asset_prices = asset_prices[1:i+2] / u
        if option_type == "call":
            option_values = np.maximum(option_values, asset_prices - K)
        else:
            option_values = np.maximum(option_values, K - asset_prices)
    return option_values[0]
