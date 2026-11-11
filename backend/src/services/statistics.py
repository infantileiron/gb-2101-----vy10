"""Site-stratified permutation test and percentile bootstrap, stdlib only."""
import hashlib, json, math, random, statistics
from collections import defaultdict
def mean(values): return statistics.fmean(values)
def quantile(values, p):
    values = sorted(values)
    k = (len(values)-1)*p
    low = math.floor(k)
    return values[low] + (values[math.ceil(k)]-values[low])*(k-low)
def pearson(x,y):
    ax,ay = mean(x),mean(y)
    dx,dy = [v-ax for v in x],[v-ay for v in y]
    divisor = math.sqrt(sum(v*v for v in dx)*sum(v*v for v in dy))
    return sum(a*b for a,b in zip(dx,dy))/divisor if divisor else None
def analyze(rows, max_loss=15, iterations=999, seed=202611):
    if not 99 <= iterations <= 4999: raise ValueError("置换次数需在99至4999之间")
    if not 0 < max_loss <= 100: raise ValueError("排除阈值无效")
    included = [r for r in rows if r["loss"] <= max_loss]
    sites = defaultdict(lambda: {"A":[],"B":[]})
    for row in included: sites[row["station"]][row["group"]].append(float(row["loss"]))
    if not sites or any(min(len(g["A"]),len(g["B"])) < 5 for g in sites.values()):
        raise ValueError("每个站点的A/B两组均需至少5条有效样本；请检查排除阈值")
    total = len(included)
    weights = {s:(len(g["A"])+len(g["B"]))/total for s,g in sites.items()}
    observed = sum(weights[s]*(mean(g["B"])-mean(g["A"])) for s,g in sites.items())
    rng = random.Random(seed)
    null,boot = [],[]
    for _ in range(iterations):
        delta = 0
        for s,g in sorted(sites.items()):
            pooled = g["A"] + g["B"]
            rng.shuffle(pooled)
            n = len(g["A"])
            delta += weights[s]*(mean(pooled[n:])-mean(pooled[:n]))
        null.append(delta)
    for _ in range(iterations):
        boot.append(sum(weights[s]*(mean(rng.choices(g["B"],k=len(g["B"])))-mean(rng.choices(g["A"],k=len(g["A"])))) for s,g in sorted(sites.items())))
    p = (1+sum(abs(v) >= abs(observed) for v in null))/(iterations+1)
    groups = []
    for label in ("A","B"):
        values = [r["loss"] for r in included if r["group"] == label]
        groups.append({"group":label,"n":len(values),"mean":mean(values),"sd":statistics.stdev(values),"q25":quantile(values,.25),"median":quantile(values,.5),"q75":quantile(values,.75)})
    histogram = []
    lower,upper = min(null),max(null)
    width = (upper-lower)/20 or 1
    for i in range(20):
        histogram.append({"x":lower+(i+.5)*width,"count":sum(lower+i*width <= v < lower+(i+1)*width or (i==19 and v==upper) for v in null)})
    return {"effect":observed,"p_value":p,"ci_low":quantile(boot,.025),"ci_high":quantile(boot,.975),"included":total,"excluded":len(rows)-total,"iterations":iterations,"seed":seed,"groups":groups,"sites":[{"station":s,"A":len(g["A"]),"B":len(g["B"]),"effect":mean(g["B"])-mean(g["A"]),"weight":weights[s]} for s,g in sorted(sites.items())],"null_histogram":histogram,"temperature_correlation":pearson([r["temperature"] for r in included],[r["loss"] for r in included]),"checksum":hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),"interpretation":"负值表示B包装失重率更低；组间差异按站点样本占比加权。p值与区间用于证据评估，不替代采购决策。"}
