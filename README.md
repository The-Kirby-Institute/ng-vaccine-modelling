# NG Vaccine Modelling
 
Code for simulating transmission of NG amogst a metapopulation representitive of Australian remote indigenous communities.

Maintained by Nicolas Rebuli ([n.rebuli@unsw.edu.au](mailto:n.rebuli@unsw.edu.au))

## Basic SIRS Model
All agents are derived from a single `person` class with population attributes `age` and `sex`. The class also has attributes for tracking `compartment` (infection status), `compatment_t0` (time of transition into current compartment) and `compartment_dt` (duration of stay in current compartment). 

The class has methods for determining `transmission_probability`, `duration_infectious` and `duration_removed` which are currently set to `0.1`, `7` and `30` but can be generalised into more relevent forms such as a function of the individual's age and gender. The class also has a method `get_infectee` for determining who one individual will infect given the event that they have triggered an infection event. This method currently just randomly samples the whole population but can be modified to incorporate biasing towards a specific sex or gender.

Transmission is simulated by simply iterating over a time vector and using the methods described above to decide when transitions between S, I and R occur.

## SIRS With Partnerships
Whereas the basic SIRS model was primarly implemented through a single `person` class, the partnerships model uses a mix of a `pandas` data frame and the old `person` class. In this version of the code, the data frame is used to store all the information about the individuals such as when they will recover from infection and who they are partnered with. An additional column stores instances of the `person` class which contains functions specific to the individual, such as `duration_infectious()` and `partnership_bias()`.

This allows the simulation code to be partially vectorised as operations such as determining whether or not an agent is still infectious reduce to simply checking an equality constraint on one column of the data frame. Operations which rely on methods from the `person` class have not been vectorised and may require replacing the methods from the person class with standalone functions in order to do so.

Transmission is simulated in two stages: partnerships and infection dynamics. Partnerships occur randomly between any two individuals and last for an exponentially distributed period of time. While partnered, transmission can occur if one individual is infectious and the other is susceptible. It turns out that epidemics are usually short lived under this parameterisation. However, if the duration of partnerships is much shorter (to reflect casual/short hookups) then epidemics can take hold.

## Anatomical Site-specific SIRS With Partnerships