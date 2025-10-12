from fastapi import APIRouter
# import spacy

from brave.api.config.db import get_engine
from brave.microbe.service import study_service
# from simstring.feature_extractor.character_ngram import CharacterNgramFeatureExtractor
# from simstring.feature_extractor.word_ngram import WordNgramFeatureExtractor

# from simstring.measure.cosine import CosineMeasure
# from simstring.database.dict import DictDatabase
# from simstring.searcher import Searcher

nlp_api = APIRouter(prefix="/nlp")

@nlp_api.post("/find-entity/{entity_id}")
async def add_tokens(entity_id):
    # nlp = spacy.load("en_core_web_sm")
    # with get_engine().begin() as conn:
    #     study = study_service.find_study_by_id(conn,entity_id)
    #     content = study["fulltext"]
    #     doc = nlp(content)
    #     sentences = list(doc.sents)
    #     # tokens =[
    #     #     [token.text for token in sent]
    #     #     for sent in sentences
    #     # ]
    #     sent =[
    #         sent.text
    #         for sent in sentences
    #     ]

        pass

@nlp_api.post("/init-db")
async def init_db():
    pass
    # db = DictDatabase(CharacterNgramFeatureExtractor(2))
    # db.add('foo')
    # db.add('bar')
    # db.add('fooo')
    # # db.save("simstring.db")
    # searcher = Searcher(db, CosineMeasure())
    # results = searcher.search('aa foo nn', 0.8)
    # print(results)