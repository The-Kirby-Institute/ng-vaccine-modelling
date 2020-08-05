# NG Vaccine Modelling
 
Code for simulating transmission of NG amogst a metapopulation representitive of Australian remote indigenous communities.

Maintained by Nicolas Rebuli ([n.rebuli@unsw.edu.au](mailto:n.rebuli@unsw.edu.au))

## Basic SIRS Model
All agents are derived from a single `person` class with population attributes `age` and `sex`. The class also has attributes for tracking `compartment` (infection status), `compatment_t0` (time of transition into current compartment) and `compartment_dt` (duration of stay in current compartment). 

The class has methods for determining `transmission_probability`, `duration_infectious` and `duration_removed` which are currently set to `0.1`, `7` and `30` but can be generalised into more relevent forms such as a function of the individual's age and gender. The class also has a method `get_infectee` for determining who one individual will infect given the event that they have triggered an infection event. This method currently just randomly samples the whole population but can be modified to incorporate biasing towards a specific sex or gender.

Transmission is simulated by simply iterating over a time vector and using the methods described above to decide when transitions between S, I and R occur.
