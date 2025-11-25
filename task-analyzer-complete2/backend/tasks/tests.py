    import unittest
    from .scoring import analyze_tasks, save_feedback, load_weights
    import datetime, os, json

    class TestScoring(unittest.TestCase):
        def test_basic_ordering(self):
            tasks = [
                {'id':'a','title':'Low effort','due_date':(datetime.date.today()+datetime.timedelta(days=10)).isoformat(),'estimated_hours':1,'importance':5,'dependencies':[]},
                {'id':'b','title':'High importance','due_date':(datetime.date.today()+datetime.timedelta(days=20)).isoformat(),'estimated_hours':5,'importance':10,'dependencies':[]},
            ]
            res = analyze_tasks(tasks, strategy='smart_balance')
            self.assertEqual(res[0]['id'], 'b')

        def test_past_due_boost(self):
            tasks = [
                {'id':'x','title':'Past due','due_date':(datetime.date.today()-datetime.timedelta(days=2)).isoformat(),'estimated_hours':5,'importance':5,'dependencies':[]},
                {'id':'y','title':'Future','due_date':(datetime.date.today()+datetime.timedelta(days=30)).isoformat(),'estimated_hours':1,'importance':5,'dependencies':[]},
            ]
            res = analyze_tasks(tasks)
            self.assertTrue(res[0]['id']=='x')

        def test_circular_detection(self):
            tasks = [
                {'id':'1','title':'T1','due_date':None,'estimated_hours':1,'importance':5,'dependencies':['2']},
                {'id':'2','title':'T2','due_date':None,'estimated_hours':1,'importance':5,'dependencies':['1']},
            ]
            res = analyze_tasks(tasks)
            self.assertEqual(res[0]['reason'], 'Circular dependency detected; manual review required.')

        def test_weekend_holiday_effect(self):
            # pick a date that is weekend (Saturday)
            today = datetime.date.today()
            # find next Saturday
            days_until_sat = (5 - today.weekday()) % 7
            sat = today + datetime.timedelta(days=days_until_sat)
            tasks = [
                {'id':'w1','title':'Weekend due','due_date':sat.isoformat(),'estimated_hours':2,'importance':5,'dependencies':[]},
                {'id':'w2','title':'Future due','due_date':(sat+datetime.timedelta(days=10)).isoformat(),'estimated_hours':2,'importance':5,'dependencies':[]},
            ]
            res = analyze_tasks(tasks)
            # weekend due should be considered slightly more urgent; expect it to rank above
            self.assertEqual(res[0]['id'], 'w1')

        def test_feedback_updates_weights(self):
            # record current weights
            pre = load_weights()
            # apply a small adjustment
            new = save_feedback({'smart_balance': {'importance': 0.05}})
            self.assertIn('smart_balance', new)
            # restore original config for cleanliness
            # write back original
            cfgpath = os.path.join(os.path.dirname(__file__), 'scoring_config.json')
            with open(cfgpath, 'w', encoding='utf-8') as f:
                json.dump({'weights':pre}, f)
if __name__ == '__main__':
    unittest.main()
