# -*- coding: utf-8 -*-


def update_infections_by_group(meta, t, i0lt, i0ht, i1lt, i1ht, i2lt, i2ht):
    i0lt[t, 0] = sum((meta.age_group == 0) & (meta.risk == 0) & (meta.site0 == 1))
    i0lt[t, 1] = sum((meta.age_group == 0) & (meta.risk == 0) & (meta.site1 == 1))
    i0lt[t, 2] = sum((meta.age_group == 0) & (meta.risk == 0) & (meta.site2 == 1))
    i0lt[t, 3] = sum((meta.age_group == 0) & (meta.risk == 0) & (meta.state == "R"))
    i0lt[t, 4] = sum((meta.age_group == 0) & (meta.risk == 0) & (meta.state == "S"))
    i0lt[t, 5] = sum((meta.age_group == 0) & (meta.risk == 0) & (meta.state == "E"))

    i0ht[t, 0] = sum((meta.age_group == 0) & (meta.risk == 1) & (meta.site0 == 1))
    i0ht[t, 1] = sum((meta.age_group == 0) & (meta.risk == 1) & (meta.site1 == 1))
    i0ht[t, 2] = sum((meta.age_group == 0) & (meta.risk == 1) & (meta.site2 == 1))
    i0ht[t, 3] = sum((meta.age_group == 0) & (meta.risk == 1) & (meta.state == "R"))
    i0ht[t, 4] = sum((meta.age_group == 0) & (meta.risk == 1) & (meta.state == "S"))
    i0ht[t, 5] = sum((meta.age_group == 0) & (meta.risk == 1) & (meta.state == "E"))


    i1lt[t, 0] = sum((meta.age_group == 1) & (meta.risk == 0) & (meta.site0 == 1))
    i1lt[t, 1] = sum((meta.age_group == 1) & (meta.risk == 0) & (meta.site1 == 1))
    i1lt[t, 2] = sum((meta.age_group == 1) & (meta.risk == 0) & (meta.site2 == 1))
    i1lt[t, 3] = sum((meta.age_group == 1) & (meta.risk == 0) & (meta.state == "R"))
    i1lt[t, 4] = sum((meta.age_group == 1) & (meta.risk == 0) & (meta.state == "S"))
    i1lt[t, 5] = sum((meta.age_group == 1) & (meta.risk == 0) & (meta.state == "E"))

    i1ht[t, 0] = sum((meta.age_group == 1) & (meta.risk == 1) & (meta.site0 == 1))
    i1ht[t, 1] = sum((meta.age_group == 1) & (meta.risk == 1) & (meta.site1 == 1))
    i1ht[t, 2] = sum((meta.age_group == 1) & (meta.risk == 1) & (meta.site2 == 1))
    i1ht[t, 3] = sum((meta.age_group == 1) & (meta.risk == 1) & (meta.state == "R"))
    i1ht[t, 4] = sum((meta.age_group == 1) & (meta.risk == 1) & (meta.state == "S"))
    i1ht[t, 5] = sum((meta.age_group == 1) & (meta.risk == 1) & (meta.state == "E"))


    i2lt[t, 0] = sum((meta.age_group == 2) & (meta.risk == 0) & (meta.site0 == 1))
    i2lt[t, 1] = sum((meta.age_group == 2) & (meta.risk == 0) & (meta.site1 == 1))
    i2lt[t, 2] = sum((meta.age_group == 2) & (meta.risk == 0) & (meta.site2 == 1))
    i2lt[t, 3] = sum((meta.age_group == 2) & (meta.risk == 0) & (meta.state == "R"))
    i2lt[t, 4] = sum((meta.age_group == 2) & (meta.risk == 0) & (meta.state == "S"))
    i2lt[t, 5] = sum((meta.age_group == 2) & (meta.risk == 0) & (meta.state == "E"))

    i2ht[t, 0] = sum((meta.age_group == 2) & (meta.risk == 1) & (meta.site0 == 1))
    i2ht[t, 1] = sum((meta.age_group == 2) & (meta.risk == 1) & (meta.site1 == 1))
    i2ht[t, 2] = sum((meta.age_group == 2) & (meta.risk == 1) & (meta.site2 == 1))
    i2ht[t, 3] = sum((meta.age_group == 2) & (meta.risk == 1) & (meta.state == "R"))
    i2ht[t, 4] = sum((meta.age_group == 2) & (meta.risk == 1) & (meta.state == "S"))
    i2ht[t, 5] = sum((meta.age_group == 2) & (meta.risk == 1) & (meta.state == "E"))

    return i0lt, i0ht, i1lt, i1ht, i2lt, i2ht


def update_prevalence(meta, t, yt):
    # Update plot vector
    yt.at[t, "S"] = sum(meta["state"]=="S")
    yt.at[t, "E"] = sum(meta["state"]=="E")
    yt.at[t, "I"] = sum(meta["state"]=="I")
    yt.at[t, "R"] = sum(meta["state"]=="R")
    yt.at[t, "site0"] = sum(meta["site0"] == 1)
    yt.at[t, "site1"] = sum(meta["site1"] == 1)
    yt.at[t, "site2"] = sum(meta["site2"] == 1)
    return yt