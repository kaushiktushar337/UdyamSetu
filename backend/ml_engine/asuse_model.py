"""ASUSE profitability adapter without sklearn/pandas/joblib dependencies.

The training-time sklearn pipeline has been exported to a compact JSON tree
ensemble for the Vercel runtime. This preserves the trained Random Forest
inference behavior while removing the multi-hundred-MB sklearn/pandas stack.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional
import json, math
from .profile_loader import BusinessProfile
from .recommendation_engine import UserBusinessContext

ASUSE_FEATURE_COLUMNS=["sector","district","location","major_nic_2dig","major_nic_5dig","ownership_type","education_level","technical_training","num_eco_activities","bank_account","est_type","years_of_operation","months_operated","daily_work_hours","accounts_maintained","used_computer","used_internet","registered","manuf_services","contract_manuf_service","franchise","total_workers","fixed_assets_owned","fixed_assets_hired","net_additions_assets"]
DEFAULT_ASUSE_VALUES={"sector":1,"district":1,"location":2,"major_nic_2dig":47,"major_nic_5dig":14105,"ownership_type":1,"education_level":3.0,"technical_training":2.0,"num_eco_activities":1,"bank_account":1,"est_type":2,"years_of_operation":1.0,"months_operated":12.0,"daily_work_hours":8.0,"accounts_maintained":2,"used_computer":2,"used_internet":2,"registered":2,"manuf_services":2,"contract_manuf_service":2.0,"franchise":2,"total_workers":1.0,"fixed_assets_owned":0.0,"fixed_assets_hired":0.0,"net_additions_assets":0.0}
NIC2_BY_CATEGORY={"food processing":10,"manufacturing":31,"services":95}
NIC2_BY_SUBCATEGORY={"bakery":10,"pickles":10,"flour milling":10,"spice processing":10,"fruit processing":10,"traditional snacks":10,"millet processing":10,"millet foods":10,"personal care products":20,"cosmetics":20,"cleaning products":20,"electronics":26,"garments":14,"footwear":15,"furniture":31,"wood products":16,"metal products":25,"personal care":96,"electronics repair":95,"digital services":62}
OUT_OF_ASUSE_SCOPE_CATEGORIES={"agriculture allied"}
@dataclass(frozen=True)
class ASUSEPrediction:
    applicable: bool; profitability_tier: Optional[str]; probabilities: Dict[str,float]; viability_score: Optional[float]; model_version: str; model_path: Optional[str]; features: Dict[str,Any]=field(default_factory=dict); inferred_features: tuple[str,...]=(); reason: str=''
    @property
    def model_used(self): return self.applicable and self.profitability_tier is not None

def _clean(v,default=0.0):
    if v is None or v=='': return default
    try: return float(v)
    except: return default

def _code(v,default):
    if v is None or v=='': return default
    try:
        n=float(v); return int(n) if n.is_integer() else n
    except: return v

def _infer_nic2(profile):
    sub=str(profile.subcategory or '').strip().lower()
    if sub in NIC2_BY_SUBCATEGORY: return NIC2_BY_SUBCATEGORY[sub]
    return NIC2_BY_CATEGORY.get(str(profile.category or '').strip().lower())

def build_asuse_features(context,profile,generated=None):
    overrides=dict(getattr(context,'asuse_overrides',{}) or {}); values=dict(DEFAULT_ASUSE_VALUES); inferred=[]
    for name,value in overrides.items():
        if name in values and value not in (None,''): values[name]=value
    for name,attr,default in [('total_workers','planned_workers',1.0),('years_of_operation','business_age_years',1.0),('daily_work_hours','daily_work_hours',8.0)]:
        if name not in overrides:
            value=getattr(context,attr,None)
            if value is not None: values[name]=max(0.0,_clean(value,default))
            else: inferred.append(name)
    if 'major_nic_2dig' not in overrides:
        nic2=_infer_nic2(profile)
        if nic2 is not None: values['major_nic_2dig']=nic2
        else: inferred.append('major_nic_2dig')
    return values,inferred

class ASUSEProfitabilityModel:
    def __init__(self,model_path='models/asuse_profitability.json'):
        p=str(model_path)
        if p.endswith('.joblib'): p=p[:-7]+'.json'
        self.model_path=p; self._model=None; self.model_version='asuse-profitability-json-v1'
    @property
    def is_loaded(self): return self._model is not None
    def load(self):
        with open(self.model_path,'r',encoding='utf-8') as f: self._model=json.load(f)
        self.model_version=str(self._model.get('version','asuse-profitability-json-v1')); return self
    def _transform(self,features):
        m=self._model; x=[]
        for i,c in enumerate(m['num_cols']):
            v=features.get(c)
            if v in (None,''): v=m['num_imputer'][i]
            v=_clean(v,m['num_imputer'][i]); scale=m['num_scale'][i] or 1.0; x.append((v-m['num_mean'][i])/scale)
        for i,c in enumerate(m['cat_cols']):
            v=features.get(c,m['cat_imputer'][i]); cats=m['cat_categories'][i]
            try: idx=cats.index(v)
            except ValueError:
                # sklearn's categorical values are often numeric but JSON may
                # represent integral values as ints; normalize that case.
                try:
                    fv=float(v); idx=next((j for j,a in enumerate(cats) if float(a)==fv),None)
                except: idx=None
            for j in range(len(cats)): x.append(1.0 if idx==j else 0.0)
        return x
    @staticmethod
    def _tree(tree,x):
        node=0
        while tree['cl'][node] != -1:
            f=tree['f'][node]
            node=tree['cl'][node] if x[f] <= tree['th'][node] else tree['cr'][node]
        vals=tree['v'][node]; total=sum(vals) or 1.0
        return [v/total for v in vals]
    def predict(self,context,profile,generated=None):
        if not self.is_loaded: self.load()
        category=str(profile.category or '').strip().lower()
        if category in OUT_OF_ASUSE_SCOPE_CATEGORIES:
            return ASUSEPrediction(False,None,{},None,self.model_version,self.model_path,reason='ASUSE is not applied to this profile because the reference category is outside the survey scope.')
        features,inferred=build_asuse_features(context,profile,generated)
        x=self._transform(features); probs=[0.0]*len(self._model['classes'])
        for tree in self._model['trees']:
            p=self._tree(tree,x)
            for i,v in enumerate(p): probs[i]+=v
        n=len(self._model['trees']) or 1; probs=[p/n for p in probs]
        probabilities={c:round(p,6) for c,p in zip(self._model['classes'],probs)}
        best=max(range(len(probs)),key=lambda i:probs[i]); prediction=self._model['classes'][best]
        anchors={'low':20.0,'medium':60.0,'high':90.0}; viability=round(sum(probabilities.get(k,0)*v for k,v in anchors.items()),2)
        return ASUSEPrediction(True,prediction,probabilities,viability,self.model_version,self.model_path,features,tuple(inferred),'ASUSE historical profitability signal generated from ASUSE-compatible establishment features.')
