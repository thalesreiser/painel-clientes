-- RNF-05: shared calendar dimension. Grain: one row per calendar day (dt_data).
-- Range: 2024-01-01 to 2028-12-31, the years covered by the seed feriados_nacionais.
-- fl_dia_util = weekday (Mon-Fri) that is not a Brazilian national holiday (no state or
-- municipal holidays). Dates are plain calendar dates; conversion to UTC-3 applies only to
-- timestamps, at presentation time (RN-03).

with dias as (

    select cast(t.d as date) as dt
    from generate_series(date '2024-01-01', date '2028-12-31', interval 1 day) as t(d)

),

-- One row per date, even if two holidays ever coincide.
feriados as (

    select
        cast(dt_feriado as date)                            as dt_feriado,
        string_agg(nm_feriado, ' / ' order by nm_feriado)   as nm_feriado,
        min(tp_feriado)                                     as tp_feriado
    from {{ ref('feriados_nacionais') }}
    group by 1

)

select
    d.dt                                                    as dt_data,
    cast(date_trunc('month', d.dt) as date)                 as dt_inicio_mes,
    cast(last_day(d.dt) as date)                            as dt_fim_mes,
    cast(extract(year from d.dt) as integer)                as nr_ano,
    cast(extract(quarter from d.dt) as integer)             as nr_trimestre,
    cast(extract(month from d.dt) as integer)               as nr_mes,
    cast(extract(day from d.dt) as integer)                 as nr_dia,
    -- ISO weekday: 1 = Monday ... 7 = Sunday
    cast(isodow(d.dt) as integer)                           as nr_dia_semana,
    isodow(d.dt) in (6, 7)                                  as fl_fim_de_semana,
    f.dt_feriado is not null                                as fl_feriado,
    f.nm_feriado,
    f.tp_feriado,
    isodow(d.dt) not in (6, 7) and f.dt_feriado is null     as fl_dia_util
from dias as d
left join feriados as f
    on f.dt_feriado = d.dt
