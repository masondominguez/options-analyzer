# content/tooltips.py

PRICING_MODELS = """
**Why Two Pricing Models?**
* **Black-Scholes (European):** Assumes the option can *only* be exercised on the exact expiration date. Great for a baseline, but slightly inaccurate for stocks.
* **Binomial Tree (American):** Factors in the probability that an option might be exercised *early* (which is allowed for U.S. stock options). This is generally the more accurate price for the options you are trading.

**Understanding Probability ITM:**
This is the market's *implied* probability that the option will expire In-The-Money, derived directly from the current Implied Volatility. It is **not** a guarantee of real-world stock movement, but rather a reflection of how the market is pricing the risk.
"""

GREEKS_CHEAT_SHEET = """
The Greeks measure how sensitive an option's price is to different market forces:

* **Delta (Direction):** How much the option price changes for a \\$1 move in the stock. A 0.30 Delta means the option gains \\$0.30 if the stock goes up \\$1. It also acts as a rough proxy for the probability of expiring In-The-Money (~30% chance).
* **Gamma (Acceleration):** How fast Delta changes. High Gamma means your position's risk profile can swing violently if the stock price suddenly moves.
* **Theta (Time Decay):** How much value the option loses every single day just by time passing. Buyers *lose* Theta; Sellers *gain* Theta.
* **Vega (Volatility):** How much the option price changes if Implied Volatility jumps by 1%. If you buy an option and IV crashes, Vega will drain your premium even if the stock moves in your direction.
"""

PAYOUT_DIAGRAM = """
This chart models your exact Profit & Loss at the moment the option expires.

* **The Green Zone:** Represents pure account profit. 
* **The Red Zone:** Represents account losses.
* **The Cap (Flat Line):** If you are a Seller, your profit is usually capped at the premium you collected. If you are a Buyer, your loss is capped at the premium you paid.
* **Opportunity Cost:** If you sell a Covered Call and the stock skyrockets, your line stays flat and green. You didn't *lose* money (you hit max profit!), you just missed out on further gains.
"""

OPTION_CHAIN = """
The **Option Chain** is the raw marketplace for options contracts at a specific expiration date. 

* **Bid vs. Ask:** The 'Bid' is what buyers are willing to pay; the 'Ask' is what sellers are demanding. The difference is the *Spread*. A tight spread means the option is highly liquid. You will usually buy at the Ask and sell at the Bid.
* **Implied Volatility (IV):** Represents the market's expectation of future price swings. High IV means the options are expensive (high premium); low IV means they are cheap.
* **Volume:** The number of contracts traded today. Always look for options with high volume so you don't get trapped in an illiquid position.
"""

IV_SURFACE = """
The **Implied Volatility (IV) Surface** is a 3D visualization of how expensive options are across different strike prices and expiration dates. It helps traders spot mispricings and gauge market fear.

To read it, break it down into two directions:

**1. The Volatility Skew (Left-to-Right along the Strike Axis)**
* **What it is:** How IV changes as you move deeper in-the-money or out-of-the-money for a *single* expiration date.
* **What to look for:** For most stocks, you will see a "smirk" shape where downside Puts have a much higher IV than upside Calls. This is because the market naturally prices in a higher premium for crash protection (fear) than for upside speculation (greed).

**2. The Term Structure (Front-to-Back along the Days to Expiration Axis)**
* **What it is:** How IV changes as you look further out in time at a *single* strike price.
* **What to look for:** Normally, IV slopes upward as time increases (contango) because more time equals more uncertainty. However, if near-term IV suddenly spikes higher than long-term IV (backwardation), it signals extreme, immediate market panic or an impending catalyst like an earnings report.

**The Cheat Sheet:**
* **High Peaks (Red/Yellow):** Options here are "expensive." Sellers love these areas; buyers should be cautious.
* **Low Valleys (Green):** Options here are "cheap." Buyers get better leverage here; sellers aren't getting paid much for the risk.
"""

CALL_POSITION_HELP = """
**Buyer**: pays premium upfront, profits when stock rises above strike, max loss = premium paid.

**Naked Call**: collects premium, max loss is theoretically unlimited if stock surges.

**Covered Call**: own 100 shares + sell this call; upside is capped at the strike but max loss is bounded — reduced by the premium received.
"""

PROBABILITIES_EXPLAINED = """
**Understanding Probability ITM:**
This is the market's *implied* probability that the option will expire In-The-Money, derived directly from the current Implied Volatility. It is **not** a guarantee of real-world stock movement, but rather a reflection of how the market is currently pricing the risk.

* **Prob. ITM (In-The-Money):** The rough chance you capture intrinsic value.
* **Prob. OTM (Out-of-The-Money):** The chance the option expires completely worthless.
"""
