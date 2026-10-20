import copy
from .core import apply_transaction,project_hash,require
class History:
    def __init__(self,project):
        self.initial=copy.deepcopy(project);self.project=copy.deepcopy(project);self.records=[];self.cursor=0;project_hash(project)
    def apply(self,transaction):
        result=apply_transaction(self.project,transaction)
        self.records=self.records[:self.cursor]+[{'before':copy.deepcopy(self.project),'after':copy.deepcopy(result['project']),'receipt':copy.deepcopy(result['receipt'])}]
        self.cursor+=1;self.project=result['project'];return result['receipt']
    def undo(self):
        require(self.cursor>0,'Nothing to undo');record=self.records[self.cursor-1];require(project_hash(self.project)==record['receipt']['after_sha256'],'History state diverged');self.project=copy.deepcopy(record['before']);self.cursor-=1;return copy.deepcopy(self.project)
    def redo(self):
        require(self.cursor<len(self.records),'Nothing to redo');record=self.records[self.cursor];require(project_hash(self.project)==record['receipt']['before_sha256'],'History state diverged');self.project=copy.deepcopy(record['after']);self.cursor+=1;return copy.deepcopy(self.project)
    def journal(self):return {'schema':'sprite-edit-journal/v1','initial_project_sha256':project_hash(self.initial),'cursor':self.cursor,'receipts':[copy.deepcopy(x['receipt'])for x in self.records]}
    @classmethod
    def replay(cls,project,journal):
        require(isinstance(journal,dict)and journal.get('schema')=='sprite-edit-journal/v1'and journal.get('initial_project_sha256')==project_hash(project),'Invalid journal precondition')
        require(isinstance(journal.get('receipts'),list)and all(isinstance(x,dict)for x in journal['receipts']),'Invalid receipts')
        require(type(journal.get('cursor'))is int and 0<=journal['cursor']<=len(journal.get('receipts',[])),'Invalid journal cursor')
        history=cls(project)
        for receipt in journal['receipts']:
            expected=history.apply(receipt['transaction']);require(expected==receipt,'Replay receipt mismatch')
        while history.cursor>journal['cursor']:history.undo()
        return history
