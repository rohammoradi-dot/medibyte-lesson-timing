"""Caption/cue timing from source ASR word intervals, without re-timing audio.
Terminology cleanup changes text only; timing remains attached to the source words.
"""
import re
import math

def _duration(value):
 value=float(value)
 if not math.isfinite(value) or value<=0:raise ValueError("duration must be finite and positive")
 return value


def sentence_units(transcript,duration,clean):
 duration=_duration(duration)
 units=[];pending=[]
 def flush():
  if not pending:return
  text=clean(''.join(w['word'] for w in pending).strip())
  start=max(0,float(pending[0]['start']));end=min(duration,float(pending[-1]['end']))
  if text and end>start:units.append(dict(start=start,end=end,text=text,words=list(pending)))
  pending.clear()
 for segment in transcript['segments']:
  words=segment.get('words') or []
  if not words:
   flush()
   text=clean(segment['text'])
   start=max(0,segment['start']);end=min(duration,segment['end'])
   if text and end>start:units.append(dict(start=start,end=end,text=text,words=[]))
   continue
  for word in words:
   if pending and word['start']<pending[-1]['start']:continue
   pending.append(word)
   # Decimal points inside a token (e.g. Cav1.3) are not sentence boundaries.
   if re.search(r'[.!?][”\'"]?$',word['word'].strip()):flush()
 flush()
 return units

def captions_from_words(units,duration,clean,is_trash):
 duration=_duration(duration)
 captions=[]
 for unit in units:
  if is_trash(unit['text']):continue
  words=unit['words']
  if not words:
   start=max(0,float(unit['start']),captions[-1]['end'] if captions else 0)
   end=min(duration,float(unit['end']))
   if end>start:captions.append(dict(start=start,end=end,text=unit['text']))
   continue
  groups=[];group=[]
  for word in words:
   group.append(word)
   last=word['word'].strip()
   span=word['end']-group[0]['start']
   if len(group)>=18 or (len(group)>=7 and (last.endswith((',', ';', ':')) or span>=6.5)):
    groups.append(group);group=[]
  if group:groups.append(group)
  for group in groups:
   text=clean(''.join(w['word'] for w in group).strip())
   start=max(0,float(group[0]['start']));end=min(duration,float(group[-1]['end']))
   if captions:start=max(start,captions[-1]['end'])
   if text and not is_trash(text) and end>start:captions.append(dict(start=round(start,3),end=round(end,3),text=text))
 return captions

def cue_events(diagram,units,duration,title):
 duration=_duration(duration)
 if not units:return []
 ids={s['id'] for s in diagram.shapes}
 fallback=[s['id'] for s in diagram.shapes if s['id'] not in ('axes','pressure-axis','volume-axis')][:4]
 def match(text):
  scored=[]
  for order,(terms,group) in enumerate(diagram.groups.items()):
   score=0
   for word in terms.lower().split():
    # Longer roots support depolarization/depolarized; short abbreviations remain exact.
    expression=r'\b'+re.escape(word)+(r'\w*' if len(word)>=5 else '')+r'\b'
    if re.search(expression,text,re.I):score+=1+min(len(word),10)/10
   if score:scored.append((score,-order,[x for x in group if x in ids]))
  return max(scored)[2] if scored else None
 events=[]
 for unit in units:
  focus=match(unit['text'])
  if not focus:continue
  at=max(0,min(duration,unit['start']))
  if events and (events[-1]['focus']==focus or at-events[-1]['start']<1.5):continue
  detail=unit['text']
  if len(detail)>240:detail=detail[:237].rsplit(' ',1)[0]+'…'
  events.append(dict(start=at,focus=focus,title=title,detail=detail))
 if not events:
  first=units[0]
  events=[dict(start=0,focus=fallback,title=title,detail=first['text'][:240])]
 events[0]['start']=0
 # Preserve a readable scaffold where a legacy diagram has few matching concepts.
 if len(events)<3:
  for fraction in (.333,.667):
   at=duration*fraction
   if all(abs(e['start']-at)>2 for e in events):
    unit=next((u for u in reversed(units) if u['start']<=at),units[0])
    events.append(dict(start=at,focus=match(unit['text']) or fallback,title=title,detail=unit['text'][:240]))
 events.sort(key=lambda e:e['start'])
 for i,event in enumerate(events):
  event['start']=round(event['start'],3)
  event['end']=round(events[i+1]['start'] if i+1<len(events) else duration,3)
 return [e for e in events if e['end']>e['start']]

def apply_progressive_reveal(diagram,cues):
 for shape in diagram.shapes:
  if shape['id'] in getattr(diagram,'progressive',()):
   onset=next((c['start'] for c in cues if shape['id'] in c['focus']),0)
   shape['introducedAt']=onset
