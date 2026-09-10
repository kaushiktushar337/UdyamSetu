"""Lightweight 384D hashed-text business matcher for Vercel."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Optional
from chatbot.embedding_model import get_embedding_model
from .profile_loader import BusinessProfile

def _dot(a,b): return sum(x*y for x,y in zip(a,b))
@dataclass
class BusinessMatch:
    profile: BusinessProfile
    semantic_score: float
    capital_score: float
    final_score: float
    reasons: List[str]
class BusinessMatcher:
    def __init__(self, model_name=None, semantic_weight=0.75, capital_weight=0.25):
        import os
        self.model_name=model_name or os.getenv('MODEL_NAME','hash-384-v1')
        self.semantic_weight=semantic_weight; self.capital_weight=capital_weight
        self.model=get_embedding_model(); self._profiles=[]; self._profile_embeddings=None
    def fit(self, profiles: Iterable[BusinessProfile]):
        self._profiles=list(profiles)
        if not self._profiles: raise ValueError('At least one business profile is required')
        self._profile_embeddings=self.model.encode([p.searchable_text() for p in self._profiles], normalize_embeddings=True)
        return self
    @staticmethod
    def _capital_score(available_capital: Optional[float], profile: BusinessProfile)->float:
        if available_capital is None: return 50.0
        required=profile.minimum_capital or profile.typical_project_cost
        if required is None or float(required)<=0: return 50.0
        ratio=max(0.0,float(available_capital))/float(required)
        return 100.0 if ratio>=1 else round(max(0.0,ratio*100),2)
    def match(self,user_text,available_capital=None,top_k=5):
        if self._profile_embeddings is None: raise RuntimeError('Call fit(profiles) before match()')
        query=self.model.encode(user_text,normalize_embeddings=True)
        matches=[]
        for profile,vec in zip(self._profiles,self._profile_embeddings):
            semantic=round((_dot(vec,query)+1)*50,2); capital=self._capital_score(available_capital,profile)
            final=round(semantic*self.semantic_weight+capital*self.capital_weight,2); reasons=[]
            if semantic>=75: reasons.append("Strong text match with the user's business interests.")
            elif semantic>=60: reasons.append("Relevant text match with the user's requirements.")
            if available_capital is not None:
                required=profile.minimum_capital or profile.typical_project_cost
                if required:
                    if available_capital>=required: reasons.append('Available capital can cover the reference project cost.')
                    else: reasons.append(f'Reference project cost exceeds available capital by approximately ₹{float(required)-float(available_capital):,.0f}.')
            matches.append(BusinessMatch(profile,semantic,capital,final,reasons))
        matches.sort(key=lambda x:x.final_score,reverse=True); return matches[:max(1,top_k)]

def build_user_business_query(interests=None,skills=None,preferences=None,location_context=None):
    parts=[]
    if interests: parts.append(f'Business interests: {interests}')
    if skills: parts.append(f'Skills and experience: {skills}')
    if preferences: parts.append(f'Preferences: {preferences}')
    if location_context: parts.append(f'Location context: {location_context}')
    text='\n'.join(parts).strip()
    if not text: raise ValueError('At least one business interest, skill, preference, or location context is required')
    return text
