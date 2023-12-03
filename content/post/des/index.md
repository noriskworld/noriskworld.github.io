This is a repost of the bolg by me dated 2018-05-21.

    #prepare the libraries
    library(tidyverse)
    library(simmer)
    library(simmer.plot)
    library(intervals)

## Simmer for R

In my short experiment with Simpy and Simmer, Simmer shines in one area:
monitoring. In Simpy a list can be passed to the simulation, and it is
flexible to choose what to code.

With Simmer, three commands `get_mon_arrivals()`,
`get_mon_attributes()`, `get_mon_resources()` can generate the story
book of the simulation. The story is in data.frame format, and can be
easily processed in R.

Let’s use the Machine Shop as an Example.

Instead of print out the events in user interface with `log_()`, we make
the simulation `invisible`, and add an attribute to log the state
(working, fail).

    machine <- function(mttf, repair_time){
          machie <- trajectory() %>% 
          # machine_state: 1-working, 0-fail
          set_attribute("machine_state", 1) %>% 
            timeout(function() rexp(1, 1/mttf)) %>% 
            set_attribute("machine_state", -1, mod="+") %>%
            seize("repairman") %>% 
            timeout(repair_time) %>% 
            release("repairman") %>% 
            set_attribute("machine_state", 1, mod="+") %>% 
            rollback(6)
      } 
    plot(machine(10,1))

<div class="grViz html-widget html-fill-item" id="htmlwidget-34a3284e932c9d2b858d" style="width:672px;height:480px;"></div>
<script type="application/json" data-for="htmlwidget-34a3284e932c9d2b858d">{"x":{"diagram":"digraph {\n\ngraph [layout = \"dot\",\n       outputorder = \"edgesfirst\",\n       bgcolor = \"white\"]\n\nnode [fontname = \"sans-serif\",\n      fontsize = \"10\",\n      shape = \"circle\",\n      fixedsize = \"true\",\n      width = \"1.5\",\n      style = \"filled\",\n      fillcolor = \"aliceblue\",\n      color = \"gray70\",\n      fontcolor = \"gray50\"]\n\nedge [fontname = \"Helvetica\",\n     fontsize = \"8\",\n     len = \"1.5\",\n     color = \"gray80\",\n     arrowsize = \"0.5\"]\n\n  \"1\" [label = \"SetAttribute\", shape = \"box\", style = \"solid\", color = \"black\", tooltip = \"keys: [machine_state], values: [1], global: 0, mod: N, init: 0\", fontcolor = \"black\", fillcolor = \"#000000\"] \n  \"2\" [label = \"Timeout\", shape = \"box\", style = \"solid\", color = \"black\", tooltip = \"delay: function()\", fontcolor = \"black\", fillcolor = \"#000000\"] \n  \"3\" [label = \"SetAttribute\", shape = \"box\", style = \"solid\", color = \"black\", tooltip = \"keys: [machine_state], values: [-1], global: 0, mod: +, init: 0\", fontcolor = \"black\", fillcolor = \"#000000\"] \n  \"4\" [label = \"Seize\", shape = \"box\", style = \"filled\", color = \"#7FC97F\", tooltip = \"resource: repairman, amount: 1\", fontcolor = \"black\", fillcolor = \"#7FC97F\"] \n  \"5\" [label = \"Timeout\", shape = \"box\", style = \"solid\", color = \"black\", tooltip = \"delay: 1\", fontcolor = \"black\", fillcolor = \"#000000\"] \n  \"6\" [label = \"Release\", shape = \"box\", style = \"filled\", color = \"#7FC97F\", tooltip = \"resource: repairman, amount: 1\", fontcolor = \"black\", fillcolor = \"#7FC97F\"] \n  \"7\" [label = \"SetAttribute\", shape = \"box\", style = \"solid\", color = \"black\", tooltip = \"keys: [machine_state], values: [1], global: 0, mod: +, init: 0\", fontcolor = \"black\", fillcolor = \"#000000\"] \n  \"8\" [label = \"Rollback\", shape = \"diamond\", style = \"filled\", color = \"lightgrey\", tooltip = \"times: -1\", fontcolor = \"black\", fillcolor = \"#D3D3D3\"] \n\"1\"->\"2\" [color = \"black\", style = \"solid\"] \n\"2\"->\"3\" [color = \"black\", style = \"solid\"] \n\"3\"->\"4\" [color = \"black\", style = \"solid\"] \n\"4\"->\"5\" [color = \"black\", style = \"solid\"] \n\"5\"->\"6\" [color = \"black\", style = \"solid\"] \n\"6\"->\"7\" [color = \"black\", style = \"solid\"] \n\"7\"->\"8\" [color = \"black\", style = \"solid\"] \n\"8\"->\"2\" [color = \"grey\", style = \"dashed\"] \n}","config":{"engine":"dot","options":null}},"evals":[],"jsHooks":[]}</script>

Make it a function.

    simmer_relia <- function(sim_time, mon_ = "attributes") {
      env <- simmer() %>% 
      # use resource to track system state
      # all items in series will require same "repair" resource. 
      # set capacity to inf, assuming no queue for repair
      # if repair resource busy -> system down
      # for n-oo-k items, if resource server > k-n ->system down 
      add_resource("repairman", capacity = Inf) %>% 
      add_generator("machine_a", machine(100, 10), at(0), mon = 2) %>% 
      add_generator("machine_b", machine(100, 5), at(0), mon = 2) %>% 
      run(sim_time) %>% 
      invisible
      if (mon_=="resources"){
        sim_log <- get_mon_resources(env)
      } else if (mon_=="attributes") {
        sim_log <- get_mon_attributes(env)
      }
      sim_log
    }

### Loop for replications

    N_RUN <-  10
    SIM_END = 500
    ptm <- proc.time()
    machine_state_log <- 1:N_RUN %>% 
      map_df(function(x) cbind(simmer_relia(SIM_END), tibble(i_run = x)))
    simmer_time <- proc.time() - ptm
    tail(machine_state_log)

    ##         time       name           key value replication i_run
    ## 211 390.6790 machine_a0 machine_state     1           1    10
    ## 212 477.4357 machine_b0 machine_state     0           1    10
    ## 213 482.4357 machine_b0 machine_state     1           1    10
    ## 214 487.5124 machine_b0 machine_state     0           1    10
    ## 215 492.5124 machine_b0 machine_state     1           1    10
    ## 216 498.2302 machine_a0 machine_state     0           1    10

Test

    simu_attributes <- simmer_relia(500)
    print(simu_attributes)

    ##         time       name           key value replication
    ## 1    0.00000 machine_a0 machine_state     1           1
    ## 2    0.00000 machine_b0 machine_state     1           1
    ## 3   10.47403 machine_a0 machine_state     0           1
    ## 4   20.47403 machine_a0 machine_state     1           1
    ## 5   83.98706 machine_b0 machine_state     0           1
    ## 6   88.98706 machine_b0 machine_state     1           1
    ## 7  121.97015 machine_a0 machine_state     0           1
    ## 8  131.97015 machine_a0 machine_state     1           1
    ## 9  132.42518 machine_b0 machine_state     0           1
    ## 10 137.42518 machine_b0 machine_state     1           1
    ## 11 138.63441 machine_b0 machine_state     0           1
    ## 12 143.63441 machine_b0 machine_state     1           1
    ## 13 253.22893 machine_a0 machine_state     0           1
    ## 14 256.61906 machine_b0 machine_state     0           1
    ## 15 261.61906 machine_b0 machine_state     1           1
    ## 16 263.22893 machine_a0 machine_state     1           1
    ## 17 294.10969 machine_a0 machine_state     0           1
    ## 18 304.10969 machine_a0 machine_state     1           1
    ## 19 331.74377 machine_a0 machine_state     0           1
    ## 20 341.74377 machine_a0 machine_state     1           1
    ## 21 347.16677 machine_b0 machine_state     0           1
    ## 22 352.16677 machine_b0 machine_state     1           1
    ## 23 377.44707 machine_a0 machine_state     0           1
    ## 24 384.29592 machine_b0 machine_state     0           1
    ## 25 387.44707 machine_a0 machine_state     1           1
    ## 26 389.29592 machine_b0 machine_state     1           1
    ## 27 392.02769 machine_b0 machine_state     0           1
    ## 28 397.02769 machine_b0 machine_state     1           1
    ## 29 453.05538 machine_a0 machine_state     0           1
    ## 30 463.05538 machine_a0 machine_state     1           1

    simu_resources <- simmer_relia(500, mon = "resources")
    plot(simu_resources, metric = "usage", "repairman", items = "server", steps = TRUE)

![](myPosts_files/figure-markdown_strict/unnamed-chunk-6-1.png)

# Monitoring: resources vs attributes

With simmer, by adding user-defined attributes, we can log the
simualtion flexibly. In the context of the system reliability, since
only one “repariman” resource is requested when ANY of the machines
fail, the “repairman” resource can be used directly for simple system
reliability metrics. If the it is series system, whenever the repairman
is busy, the system is down. Or it is n-out-of-k, then &gt;= n
simultaneous “repairs” implies system down.

The attribute logs the state of all the “machines”, it is more flexible
to use the attributes. We are interest in the event sequence of the
system down time, the `Intervals` pacakge, which provides a collections
of operation on intervals over the real number line (R), is helpful the
determine the system state base on the component state.

In the example above, we have the event sequence of the machine\_a and
machine\_b, so for a parellel system, the intersection of downtime
interval is the system down time. and for a series system, union.

### Convert event sequences to state intervals

    machine_state_interval <- function(machine_state_log){
      machine_state_log %>%
        group_by(i_run, name) %>% 
        arrange(time) %>% 
        # end_time is lead(start_time) (remove leading NA), last one is sim_end
        mutate(end_time = c(head(lead(time), -1), SIM_END)) %>% 
        ungroup() %>% 
        dplyr::select(name, value, start_time = time, end_time, i_run) %>% 
        arrange(i_run, name, start_time)
    }

    state_interval <- machine_state_interval(machine_state_log)

    machine_down_interval <- function(state_interval, i, machine_name){
      fail_log <- state_interval %>% 
        filter(i_run == i, name == machine_name) %>% 
        filter(value == 0)
      Intervals(matrix(c(fail_log$start_time,fail_log$end_time), ncol = 2))
    } 

### parallel -&gt; intersection of the interval

    parallel_down_log <- tibble(start_time = as.numeric(), end_time = as.numeric(), i_run = as.integer())

    for (i in 1:N_RUN){
      parallel_down_interval <- interval_intersection(
        machine_down_interval(state_interval, i, "machine_a0"), 
        machine_down_interval(state_interval, i, "machine_b0") )
      if(length(parallel_down_interval) > 0){
        print(i)
        print(parallel_down_interval)
        parallel_down_log <- rbind(parallel_down_log, 
                                cbind(as.matrix(parallel_down_interval), tibble(i_run = i)))
      }
    }

    ## [1] 2
    ## Object of class Intervals
    ## 1 interval over R:
    ## [267.642361471865, 271.202494973753]
    ## [1] 4
    ## Object of class Intervals
    ## 2 intervals over R:
    ## [59.6691804141208, 62.8458826523274]
    ## [63.2973465323448, 68.2973465323448]
    ## [1] 6
    ## Object of class Intervals
    ## 1 interval over R:
    ## [82.2008423744411, 87.2008423744411]
    ## [1] 8
    ## Object of class Intervals
    ## 3 intervals over R:
    ## [115.679148485481, 117.919104616613]
    ## [243.891257849502, 246.206763600052]
    ## [284.118580658973, 289.118580658973]

    names(parallel_down_log) <- c("start", "end", "i_run")
    print(parallel_down_log)

    ##       start       end i_run
    ## 1 267.64236 271.20249     2
    ## 2  59.66918  62.84588     4
    ## 3  63.29735  68.29735     4
    ## 4  82.20084  87.20084     6
    ## 5 115.67915 117.91910     8
    ## 6 243.89126 246.20676     8
    ## 7 284.11858 289.11858     8

### Series -&gt; union of the interval

    series_down_log <- tibble(start_time = as.numeric(), end_time = as.numeric(), i_run = as.integer())

    for (i in 1:N_RUN){
      series_down_interval <- interval_union(
        machine_down_interval(state_interval, i, "machine_a0"), 
        machine_down_interval(state_interval, i, "machine_b0") )
      if(length(series_down_interval) > 0){
        series_down_log <- rbind(series_down_log, 
                                 cbind(as.matrix(series_down_interval), tibble(i_run = i)))
      }
    }
    names(series_down_log) <- c("start", "end", "i_run")
    head(series_down_log,20)

    ##         start       end i_run
    ## 1   28.623260  33.62326     1
    ## 2  215.470801 225.47080     1
    ## 3  286.300669 291.30067     1
    ## 4  294.876674 299.87667     1
    ## 5  377.558755 387.55875     1
    ## 6  438.039076 448.03908     1
    ## 7  261.202495 272.64236     2
    ## 8  311.408619 316.40862     2
    ## 9  325.412461 330.41246     2
    ## 10 358.208931 368.20893     2
    ## 11 456.212030 461.21203     2
    ## 12  16.000713  21.00071     3
    ## 13  33.613019  43.61302     3
    ## 14  67.380602  72.38060     3
    ## 15 413.725648 418.72565     3
    ## 16 420.672977 430.67298     3
    ## 17 438.382483 443.38248     3
    ## 18 493.668162 500.00000     3
    ## 19   9.118958  19.11896     4
    ## 20  21.141130  31.14113     4
