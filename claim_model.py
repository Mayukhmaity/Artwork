import spacy
from spacy.matcher import PhraseMatcher
import pandas as pd

nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab)
terms = ["WHEAT", "BARLEY", "RYE", "OATS", "SPELT", "KAMUT", "MILK"]
# Only run nlp.make_doc to speed things up
patterns = [nlp.make_doc(text) for text in terms]
matcher.add("TerminologyList", patterns)

doc = nlp("Water, rapeseed oil, sour cream (8%) (MILK), spirit vinegar, modified starch, EGG yolk, yoghurt powder (MILK), salt, sugar, acid (lactic")
matches = matcher(doc)
for match_id, start, end in matches:
    span = doc[start:end]
    print(span.text)