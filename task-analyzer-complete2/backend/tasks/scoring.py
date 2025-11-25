import datetime
from typing import List, Dict, Tuple, Any
import json, os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'scoring_config.json')

DEFAULT_WEIGHTS = {
    'smart_balance': {'urgency':0.35,'importance':0.35,'effort':0.15,'dependency':0.15},
    'fastest_wins': {'urgency':0.1,'importance':0.2,'effort':0.6,'dependency':0.1},
    'high_impact': {'urgency':0.1,'importance':0.7,'effort':0.1,'dependency':0.1},
    'deadline_driven': {'urgency':0.6,'importance':0.2,'effort':0.1,'dependency':0.1}
}

HOLIDAYS = [
    # Simple example holidays (ISO dates) - expand as needed
    '2025-01-26', '2025-08-15', '2025-10-02'
]

def load_weights():
    try:
        with open(CONFIG_PATH,'r',encoding='utf-8') as f:
            cfg = json.load(f)
        return cfg.get('weights', DEFAULT_WEIGHTS)
    except Exception:
        return DEFAULT_WEIGHTS

def save_feedback(adjustments: Dict):
    """Adjust weights based on user feedback. adjustments is a dict of {strategy: {component: delta}}"""
    cfg = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH,'r',encoding='utf-8') as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
    weights = cfg.get('weights', DEFAULT_WEIGHTS)
    # apply simple additive adjustments and renormalize per strategy
    for strat, changes in adjustments.items():
        if strat not in weights:
            weights[strat] = DEFAULT_WEIGHTS.get(strat, DEFAULT_WEIGHTS['smart_balance']).copy()
        for comp, delta in changes.items():
            weights[strat][comp] = max(0.0, weights[strat].get(comp,0.0) + float(delta))
        # renormalize
        total = sum(weights[strat].values()) or 1.0
        for comp in weights[strat]:
            weights[strat][comp] = weights[strat][comp] / total
    cfg['weights'] = weights
    with open(CONFIG_PATH,'w',encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)
    return weights

def is_holiday_or_weekend(date: datetime.date) -> bool:
    if date is None:
        return False
    # weekend (Sat/Sun) or listed holiday
    if date.weekday() >= 5:
        return True
    if date.isoformat() in HOLIDAYS:
        return True
    return False

def detect_cycle(tasks: List[Dict]) -> Tuple[bool, List]:
    # basic cycle detection using DFS on dependency graph
    nodes = {}
    for idx, t in enumerate(tasks):
        key = str(t.get('id', idx))
        nodes[key] = [str(d) for d in t.get('dependencies', [])]
    visited = {}
    def dfs(n, stack):
        if n in stack:
            return True
        if n in visited:
            return False
        visited[n] = True
        stack.add(n)
        for nei in nodes.get(n, []):
            if dfs(nei, stack):
                return True
        stack.remove(n)
        return False
    for n in nodes:
        if dfs(n, set()):
            return True, []
    return False, []

def normalize(val, minv, maxv):
    if maxv - minv == 0:
        return 0.0
    return (val - minv) / (maxv - minv)

def analyze_tasks(tasks: List[Dict], strategy: str='smart_balance') -> List[Dict]:
    """Calculate priority scores for a list of tasks and return sorted list.
    Each returned task dict will include 'score' and 'reason'.
    Strategies are configurable via scoring_config.json and can be updated via save_feedback.
    """
    weights_all = load_weights()
    weights = weights_all.get(strategy, weights_all.get('smart_balance'))
    # Defensive copy & validation
    sanitized = []
    today = datetime.date.today()
    for idx, t in enumerate(tasks):
        task = dict(t)  # shallow copy
        task.setdefault('title', f'Untitled {idx}')
        task.setdefault('due_date', None)
        if isinstance(task['due_date'], str):
            try:
                task['due_date'] = datetime.date.fromisoformat(task['due_date'])
            except Exception:
                task['due_date'] = None
        task.setdefault('estimated_hours', 1.0)
        task.setdefault('importance', 5)
        task.setdefault('dependencies', [])
        task.setdefault('id', str(idx))
        sanitized.append(task)
    # detect cycles
    has_cycle, _ = detect_cycle(sanitized)
    if has_cycle:
        for task in sanitized:
            task['score'] = 100.0
            task['reason'] = 'Circular dependency detected; manual review required.'
        return sanitized
    # compute raw scores
    urgencies = []
    importances = []
    efforts = []
    dependents_count = {t['id']:0 for t in sanitized}
    for t in sanitized:
        for dep in t.get('dependencies', []):
            dep = str(dep)
            if dep in dependents_count:
                dependents_count[dep] += 1
    for t in sanitized:
        if t['due_date'] is None:
            days = 365
        else:
            days = (t['due_date'] - today).days
            # if due date falls on weekend/holiday, consider it slightly earlier (more urgent)
            if is_holiday_or_weekend(t['due_date']):
                days -= 0.5
        imp = max(1, min(10, int(t.get('importance', 5))))
        eff = max(0.1, float(t.get('estimated_hours', 1.0)))
        depc = dependents_count.get(t['id'], 0)
        urgencies.append(days)
        importances.append(imp)
        efforts.append(eff)
        t['_raw'] = {'days': days, 'importance': imp, 'effort': eff, 'dependents': depc}
    # normalize ranges
    min_days, max_days = min(urgencies), max(urgencies)
    min_imp, max_imp = min(importances), max(importances)
    min_eff, max_eff = min(efforts), max(efforts)
    min_dep = min(d.get('_raw')['dependents'] for d in sanitized)
    max_dep = max(d.get('_raw')['dependents'] for d in sanitized)
    for t in sanitized:
        raw = t['_raw']
        if raw['days'] < 0:
            urgency_score = 1.0 + min(1.0, -raw['days'] / 30.0)
        else:
            urgency_score = 1.0 - normalize(raw['days'], min_days, max_days)
        importance_score = normalize(raw['importance'], min_imp, max_imp)
        effort_score = 1.0 - normalize(raw['effort'], min_eff, max_eff)
        dependency_score = normalize(raw['dependents'], min_dep, max_dep)
        # apply weights from config
        w_urg = weights.get('urgency', 0.35)
        w_imp = weights.get('importance', 0.35)
        w_eff = weights.get('effort', 0.15)
        w_dep = weights.get('dependency', 0.15)
        score = (w_urg * urgency_score +
                 w_imp * importance_score +
                 w_eff * effort_score +
                 w_dep * dependency_score) * 100.0
        if raw['days'] < 0:
            score += 5.0
        t['score'] = round(score, 2)
        reasons = []
        reasons.append(f"Urgency:{round(urgency_score,2)}")
        reasons.append(f"Importance:{round(importance_score,2)}")
        reasons.append(f"EffortBenefit:{round(effort_score,2)}")
        if raw['dependents']>0:
            reasons.append(f"Blocks:{raw['dependents']} tasks")
        t['reason'] = '; '.join(reasons)
    sorted_tasks = sorted(sanitized, key=lambda x: x['score'], reverse=True)
    return sorted_tasks
