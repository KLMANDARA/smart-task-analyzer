import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .scoring import analyze_tasks, save_feedback
from django.views.decorators.http import require_GET, require_POST

@csrf_exempt
@require_POST
def analyze(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
        tasks = body.get('tasks') or body
        strategy = body.get('strategy', 'smart_balance') if isinstance(body, dict) else 'smart_balance'
        result = analyze_tasks(tasks, strategy=strategy)
        return JsonResponse({'tasks': result}, safe=False)
    except Exception as e:
        return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type='application/json')

@require_GET
def suggest(request):
    strategy = request.GET.get('strategy', 'smart_balance')
    sample = request.GET.get('sample')
    try:
        tasks = json.loads(sample) if sample else []
    except Exception:
        tasks = []
    analyzed = analyze_tasks(tasks, strategy=strategy) if tasks else []
    top3 = analyzed[:3]
    out = []
    for t in top3:
        out.append({
            'id': t.get('id'),
            'title': t.get('title'),
            'score': t.get('score'),
            'reason': t.get('reason')
        })
    return JsonResponse({'suggestions': out})

@csrf_exempt
@require_POST
def feedback(request):
    """Accept feedback JSON:
    { "strategy": "smart_balance", "adjustments": {"urgency": 0.05, "importance": -0.02} }
    Or for multiple strategies: { "adjustments": { "smart_balance": {"urgency":0.05} } }
    """
    try:
        body = json.loads(request.body.decode('utf-8'))
        if 'adjustments' in body and isinstance(body['adjustments'], dict):
            adjustments = body['adjustments']
            # if top-level keys are components, wrap them under strategy
            if set(adjustments.keys()) & {'urgency','importance','effort','dependency'}:
                strategy = body.get('strategy','smart_balance')
                adjustments = {strategy: adjustments}
            new_weights = save_feedback(adjustments)
            return JsonResponse({'status':'ok','weights': new_weights})
        else:
            return HttpResponseBadRequest(json.dumps({'error':'invalid payload'}), content_type='application/json')
    except Exception as e:
        return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type='application/json')
