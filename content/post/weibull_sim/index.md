## Problem statement

    library(tidyverse)

    ## ── Attaching core tidyverse packages ──────────────────────── tidyverse 2.0.0 ──
    ## ✔ dplyr     1.1.4     ✔ readr     2.1.4
    ## ✔ forcats   1.0.0     ✔ stringr   1.5.1
    ## ✔ ggplot2   3.4.4     ✔ tibble    3.2.1
    ## ✔ lubridate 1.9.3     ✔ tidyr     1.3.0
    ## ✔ purrr     1.0.2     
    ## ── Conflicts ────────────────────────────────────────── tidyverse_conflicts() ──
    ## ✖ dplyr::filter() masks stats::filter()
    ## ✖ dplyr::lag()    masks stats::lag()
    ## ℹ Use the conflicted package (<http://conflicted.r-lib.org/>) to force all conflicts to become errors

    library(stringr)

The script below is trying to generate warranty return data for a
product that follows a Weibull time-to-failure distribution.

We further assume that: - `shipment per day` is constant, and there is
no delay in deploy in the field. - return data is immediate and
accurate - A serial number will be genreated for each shipped product.

The function will take the following input: - Weibull parameters, eta
and beta - ship\_date\_start, ship\_date\_end - report\_stop\_date
(either end of warranty, or end of analysis period) - shipment per day

All dates will be in `ymd` format

    return_gen <- function(eta, 
                           beta, 
                           ship_date_start, 
                           ship_date_end, 
                           shipment_per_day, 
                           stop_date
                           ){
      date_seriers = seq.Date(ymd(ship_date_start), ymd(ship_date_end), "days")
      stop_date = ymd(stop_date)
      n_days = length(date_seriers)
      data <- tibble(ship_date = rep(date_seriers, shipment_per_day),
                     time2failure = rweibull(n_days * shipment_per_day, beta, eta),
      ) %>% 
        mutate(fail_date = ship_date + duration(hours = time2failure),
              status = if_else(fail_date > stop_date, "S", "F"),
              return_date = if_else(fail_date > stop_date, as.Date(stop_date), as.Date(fail_date)),
              reported_hours = as.numeric(interval(ship_date, return_date), "hours")) %>% 
        arrange(ship_date) %>% 
        mutate(SN = str_c(as.character(ship_date), rep(str_pad(1:shipment_per_day, 6, pad="0"), n_days), sep="-")
               )
              
        return(data)
    }

    data <- return_gen(eta = 50000, 
                       beta = 3,
                       ship_date_start = 20210101, 
                       ship_date_end = 20211231,
                       shipment_per_day = 10,
                       stop_date = 20230630
    )

    data

    ## # A tibble: 3,650 × 7
    ##    ship_date  time2failure fail_date           status return_date reported_hours
    ##    <date>            <dbl> <dttm>              <chr>  <date>               <dbl>
    ##  1 2021-01-01       21063. 2023-05-28 15:12:21 F      2023-05-28           21048
    ##  2 2021-01-01        9528. 2022-02-02 00:07:30 F      2022-02-02            9528
    ##  3 2021-01-01       52230. 2026-12-17 05:34:50 S      2023-06-30           21840
    ##  4 2021-01-01       77734. 2029-11-13 22:26:13 S      2023-06-30           21840
    ##  5 2021-01-01       54276. 2027-03-12 12:01:16 S      2023-06-30           21840
    ##  6 2021-01-01       11563. 2022-04-27 19:27:18 F      2022-04-27           11544
    ##  7 2021-01-01       47750. 2026-06-13 14:15:04 S      2023-06-30           21840
    ##  8 2021-01-01       26992. 2024-01-30 16:25:10 S      2023-06-30           21840
    ##  9 2021-01-01       41921. 2025-10-13 17:13:06 S      2023-06-30           21840
    ## 10 2021-01-01       14455. 2022-08-26 06:51:43 F      2022-08-26           14448
    ## # ℹ 3,640 more rows
    ## # ℹ 1 more variable: SN <chr>

Note that the `echo = FALSE` parameter was added to the code chunk to
prevent printing of the R code that generated the plot.

We fit the Weibull distribution with the simulated data using the
`Survival` package.

> survreg’s scale parameter = 1/(rweibull shape parameter) survreg’s
> intercept = log(rweibull scale parameter)

    library(survival)


    weib_fit <- function (surv_data){
      test_fit <- survival::survreg(Surv(time, status) ~ 1,
                                    data = surv_data,
                                    dist = "weibull"
                                    )
      beta_fit = 1 / (test_fit$scale)
      eta_fit = exp(test_fit$coefficients[[1]])
      return(tibble(beta_fit, eta_fit))
    }

    surv_data <- data %>% 
      mutate(censored = if_else(status == "F", 1, 0)) %>% 
      select(time = reported_hours, status = censored)

    fitted <- weib_fit(surv_data)
    print(fitted)

    ## # A tibble: 1 × 2
    ##   beta_fit eta_fit
    ##      <dbl>   <dbl>
    ## 1     3.00  49448.

We repeat the simulation for several times to see how well the regession
fit the underlying model.

    N_SIM = 8
    fitted = tibble(id=as.integer(), beta_fit = as.numeric(), eta_fit = as.numeric())
    for (i in 1:N_SIM){
      data <- return_gen(eta = 50000, 
                       beta = 3,
                       ship_date_start = 20210101, 
                       ship_date_end = 20211231,
                       shipment_per_day = 10,
                       stop_date = 20230630 )
      surv_data <- data %>% 
      mutate(censored = if_else(status == "F", 1, 0)) %>% 
      select(time = reported_hours, status = censored)
      fitted <- fitted %>% add_row(id = i, weib_fit(surv_data))
    }
    print(fitted)

    ## # A tibble: 8 × 3
    ##      id beta_fit eta_fit
    ##   <int>    <dbl>   <dbl>
    ## 1     1     3.01  50176.
    ## 2     2     2.93  50123.
    ## 3     3     2.73  53022.
    ## 4     4     2.66  59231.
    ## 5     5     2.93  50356.
    ## 6     6     3.38  43154.
    ## 7     7     2.96  51364.
    ## 8     8     2.85  52744.
