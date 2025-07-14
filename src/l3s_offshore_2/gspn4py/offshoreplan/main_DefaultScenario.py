# Clear variables
globals().clear()
import pandas as pd
from makeDefaultScenario import make_default_scenario
from utils.updateScenario import update_scenario
from fmain import fmain



# Run setup
all_results = pd.DataFrame()

# Assuming makeGenScenario(), updateScenario(), and fmain() are defined somewhere
scenario = make_default_scenario()
scenario = update_scenario(scenario)

# Run
results, all_results = fmain(scenario, all_results)

print(f"Construction took {results['traceStateX1'][-1]['currentDate'] - results['traceStateX1'][-1]['startDate']} hours")

# Create and write last state on hard disk for reimport to the Manager
with open('lastState.txt', 'wt') as f_last:
    f_last.write(str(results['traceStateX1'][-1]))

with open('solutions/plans/plan_gen.py', 'wt') as fname:
    fname_tex = 'solutions/plans/plan_gen-LaTeX.txt'

    fname.write(str(results['applied_all']))
    
    # Write to LaTeX file
    with open(fname_tex, 'wt') as f_tex:
        f_tex.write(writePlanToFile_LaTeX(results))