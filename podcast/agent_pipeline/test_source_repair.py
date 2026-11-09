import copy
import unittest
from .source_repair import repair_targets,merge_source_repair,repair_prompt

class RepairTests(unittest.TestCase):
    def setUp(self):
        self.old={'run_id':'old','date':'2026-11-09','context_hash':'abc','status':'research_blocked',
                  'research':[{'role':'world','stories':[{'id':'story','headline':'unchanged'}],
                    'sources':[{'id':'s','url':'https://example.org/a','status':'partial','attempted_at':None}]}]}
        self.targets=repair_targets(self.old['research'])
        self.update={'sources':[{'source_id':'s','url':'https://example.org/a','status':'blocked','notes':'Login required'}]}
        self.kw=dict(targets=self.targets,edition_date='2026-11-09',context_hash='abc',new_run_id='new')
        self.trace=[dict(event='item.completed',action='open_page',status='completed',url='https://example.org/a',timestamp_basis='adapter_observed',observed_at='2026-11-09T01:00:00Z',trace_id='trace')]
    def test_merge_immutable(self):
        before=copy.deepcopy(self.old)
        result=merge_source_repair(self.old,self.update,self.trace,**self.kw)
        self.assertEqual(self.old,before)
        self.assertEqual(result['research'][0]['stories'],before['research'][0]['stories'])
        self.assertEqual(result['research'][0]['sources'][0]['trace_ids'],['trace'])
        self.assertEqual(result['status'],'research_blocked')
        self.assertEqual(result['parent_run_id'],'old')
    def test_reject_changed_url_unknown_id_stories(self):
        for field,value in [('url','https://example.org/b'),('source_id','other')]:
            data=copy.deepcopy(self.update);data['sources'][0][field]=value
            with self.assertRaises(ValueError):merge_source_repair(self.old,data,self.trace,**self.kw)
        data=copy.deepcopy(self.update);data['stories']=[]
        with self.assertRaises(ValueError):merge_source_repair(self.old,data,self.trace,**self.kw)
    def test_reject_date_context_run(self):
        for field,value in [('edition_date','2026-11-10'),('context_hash','other'),('new_run_id','old')]:
            with self.assertRaises(ValueError):merge_source_repair(self.old,self.update,self.trace,**dict(self.kw,**{field:value}))
    def test_refresh_local_intake_preserves_web(self):
        self.old['research'][0]['sources'].append({'id':'upstream','url':'','source_kind':'local_file','attempted_at':'old'})
        intake=[{'source_id':'upstream','source_kind':'local_file','path':'archive/2026-11-09.json',
                 'sha256':'a'*64,'observed_at':'2026-11-09T02:00:00Z','timestamp_basis':'host_read'}]
        result=merge_source_repair(self.old,{'sources':[]},[],**self.kw,intake_events=intake)
        sources=result['research'][0]['sources']
        self.assertEqual(sources[0],self.old['research'][0]['sources'][0])
        self.assertEqual(sources[1]['host_evidence'],intake[0])
        self.assertEqual(self.old['research'][0]['sources'][1]['attempted_at'],'old')
        self.assertIn('Independent unaffected hosts may still be attempted',repair_prompt(self.targets))

    def test_no_trace_no_timestamp(self):
        result=merge_source_repair(self.old,self.update,[],**self.kw)
        self.assertIsNone(result['research'][0]['sources'][0]['attempted_at'])
    def test_unattempted_policy_and_security(self):
        self.old['research'][0]['sources'][0]['status']='unattempted'
        self.assertEqual(repair_targets(self.old['research']),[])
        self.assertEqual(len(repair_targets(self.old['research'],required_source_ids=['s'])),1)
        self.assertEqual(repair_targets(self.old['research'],required_source_ids=['s'],security_blocked=True),[])
        self.assertIn('Do not return timestamps',repair_prompt(self.targets))

if __name__=='__main__':unittest.main()
