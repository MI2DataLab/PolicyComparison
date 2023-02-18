from gensim import models
from gensim.corpora.dictionary import Dictionary
from contextualized_topic_models.models.ctm import CombinedTM
from contextualized_topic_models.utils.data_preparation import TopicModelDataPreparation

from typing import List, Union
import pandas as pd


class Model:
    def __init__(self, 
                 num_topics: int,
                 docs: Union[pd.Series, List[List[str]]],
                 encoded_docs: Union[pd.Series, List[List[str]]],
                 model_type: str = "lda",
                 random_state: int = 42,
                 **kwargs): 
        self.model_type = model_type
        self.encoded_docs = encoded_docs
        self.num_topics = num_topics

        if self.model_type == "lda":
            self.int_model = models.LdaMulticore(
                corpus= self.encoded_docs,
                num_topics=num_topics,
                random_state=random_state,
                passes=kwargs.get("passes", 8),
                iterations=kwargs.get("iterations", 100),
                alpha=kwargs.get("alpha", "symmetric"),
            )
        elif self.model_type == "nmf":
            self.int_model = models.Nmf(
                corpus=self.encoded_docs,
                num_topics=num_topics,
                random_state=random_state,
                passes=kwargs.get("passes", 8),
                kappa=kwargs.get("kappa", 1.0),
            )
        elif self.model_type == "ctm":
            tp = TopicModelDataPreparation(kwargs.get("contextualized_model", "paraphrase-distilroberta-base-v2"))
            training_dataset = tp.fit(text_for_contextual=docs, text_for_bow=encoded_docs)
            self.int_model =  CombinedTM(bow_size=len(tp.vocab), contextual_size=kwargs.get("contextual_size", 768), 
                             n_components=num_topics)
            self.int_model.fit(training_dataset) 

    def get_topics(self, num_words: int = 10) -> pd.DataFrame:
        if self.model_type == "lda" or self.model_type == "nmf":
            return self.int_model.show_topics(
                num_topics=self.int_model.num_topics,
                num_words=num_words,
                formatted=False,
                )
        elif self.model_type == "ctm":
            pass
    
    def get_topics_list(self, dictionary: Dictionary, num_words: int = 20) -> List[List[str]]:
        if self.model_type == "lda" or self.model_type == "nmf":
            if not dictionary.id2token:
                dictionary.id2token = {v: k for k, v in dictionary.token2id.items()}

            topics_list = []
            for topic in self.int_model.get_topics():
                best_n_words_ids = topic.argsort()[::-1][:num_words]
                best_n_words = [dictionary.id2token[_id] for _id in best_n_words_ids]
                topics_list.append(best_n_words)
            return topics_list
        elif self.model_type == "ctm":
            pass
        
    def get_topic_probs(self, corpus: Union[pd.Series, List[List[str]]]) -> pd.DataFrame:
        if self.model_type == "lda" or self.model_type == "nmf":
            return self.int_model[corpus]
        elif self.model_type == "ctm":
            pass

    def get_term_topics(self, word_id: int, min_prob: float = 0) -> pd.DataFrame:
        if self.model_type == "lda" or self.model_type == "nmf":
            return self.int_model.get_term_topics(word_id, min_prob)
        elif self.model_type == "ctm":
            pass
                
    def save(self, path):
        if self.model_type == "lda" or self.model_type == "nmf":
            self.int_model.save(path)
        elif self.model_type == "ctm":
            pass