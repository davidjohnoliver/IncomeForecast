# IncomeForecast

IncomeForecast is a program that models income and savings over the course of your career, and tries to calculate how much money you need to save for retirement. It can also try to find the optimal way that savings should be split between different investment types.

IncomeForecast's tax regime and available investment types are specific to Québec, Canada, because that's where the author lives.

IncomeForecast is provided as-is. It may have undiscovered bugs, it certainly doesn't cover all possible scenarios, and trying to forecast your income in 10 years' time is inevitably highly uncertain. Don't blindly rely on it, is what I'm saying.

## Running the program

1. Open the `IncomeForecast.ipynb` notebook.
2. Set values in the 'Configuration' section according to the simulation you want to run. Make sure to set all parameters marked `set.this.value`.
3. Run the cell to run the simulation and display the results.

## Architecture

See a [technical summary](architecture.md) of the internal architecture of the program.