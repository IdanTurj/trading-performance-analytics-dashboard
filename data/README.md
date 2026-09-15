# Dataset

`BTCUSDT_simulation_results.csv` is a compact historical sample of trading-simulation outputs used by the dashboard.

Important fields include:

- `symbol` - simulated trading pair
- `startMonth` / `endMonth` - simulation period
- `leverage` - leverage parameter
- `wager` / `wagerMultiplayer` - position-sizing parameters
- `tpDiversionX100` - take-profit configuration
- `slDiversionMultiplayer100` - stop-loss configuration
- `balance` - ending balance
- `minBalance` / `maxBalance` - observed balance range
- `winNumber` / `errorNumber` - winning and losing outcomes
- `maxPosition` - maximum position exposure

The application derives `totalTrades`, `winRate`, and `balanceRange` from these fields.

This public sample is intentionally limited to the columns needed for the portfolio analysis and contains no credentials or private infrastructure data.
