"""
This examples trains BERT (or any other transformer model like RoBERTa, DistilBERT etc.) for the STSbenchmark from scratch. It generates sentence embeddings
that can be compared using cosine-similarity to measure the similarity.
Usage:
python training_nli.py
OR
python training_nli.py pretrained_transformer_model_name
"""
from torch.utils.data import DataLoader
import math
from sentence_transformers import SentenceTransformer,  SentencesDataset, LoggingHandler, losses, models, util
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from sentence_transformers.readers import STSBenchmarkDataReader, InputExample
import logging
from datetime import datetime
import sys
import os
import gzip
import csv

#### Just some code to print debug information to stdout
logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    handlers=[LoggingHandler()])
#### /print debug information to stdout


#You can specify any huggingface/transformers pre-trained model here, for example, bert-base-uncased, roberta-base, xlm-roberta-base
model_name = 'ETRI_KoBERT/003_bert_eojeol_pytorch'

# Read the dataset
train_batch_size = 16
num_epochs = 4
model_save_path = 'output/training_stsbenchmark_'+model_name.replace("/", "-")+'-'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Use Huggingface/transformers model (like BERT, RoBERTa, XLNet, XLM-R) for mapping tokens to embeddings
word_embedding_model = models.Transformer(model_name, isKor=True)

# Apply mean pooling to get one fixed sized sentence vector
pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension(),
                               pooling_mode_mean_tokens=True,
                               pooling_mode_cls_token=False,
                               pooling_mode_max_tokens=False)

model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

# Convert the dataset to a DataLoader ready for training
logging.info("Read STSbenchmark train dataset")

train_samples = []
dev_samples = []
test_samples = []

with open('./KorNLUDatasets/KorSTS/tune_dev.tsv', 'rt', encoding='utf-8') as fIn:
    lines = fIn.readlines()
    for line in lines:
        s1, s2, score = line.split('\t')
        score = score.strip()
        score = float(score) / 5.0
        dev_samples.append(InputExample(texts= [s1,s2], label=score))

with open('./KorNLUDatasets/KorSTS/tune_test.tsv', 'rt', encoding='utf-8') as fIn:
    lines = fIn.readlines()
    for line in lines:
        s1, s2, score = line.split('\t')
        score = score.strip()
        score = float(score) / 5.0
        test_samples.append(InputExample(texts= [s1,s2], label=score))

with open('./KorNLUDatasets/KorSTS/tune_train.tsv', 'rt', encoding='utf-8') as fIn:
    lines = fIn.readlines()
    for line in lines:
        s1, s2, score = line.split('\t')
        score = score.strip()
        score = float(score) / 5.0
        train_samples.append(InputExample(texts= [s1,s2], label=score))

train_dataset = SentencesDataset(train_samples, model)
train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=train_batch_size)
train_loss = losses.CosineSimilarityLoss(model=model)


logging.info("Read STSbenchmark dev dataset")
evaluator = EmbeddingSimilarityEvaluator.from_input_examples(dev_samples, name='sts-dev')


# Configure the training. We skip evaluation in this example
warmup_steps = math.ceil(len(train_dataset) * num_epochs / train_batch_size * 0.1) #10% of train data for warm-up
logging.info("Warmup-steps: {}".format(warmup_steps))


# Train the model
model.fit(train_objectives=[(train_dataloader, train_loss)],
          evaluator=evaluator,
          epochs=num_epochs,
          evaluation_steps=1000,
          warmup_steps=warmup_steps,
          output_path=model_save_path)


##############################################################################
#
# Load the stored model and evaluate its performance on STS benchmark dataset
#
##############################################################################

#word_embedding_model = models.Transformer(model_save_path)

#pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension(),
#        pooling_mode_mean_tokens=True,
#        pooling_mode_cls_token=False,
#        pooling_mode_max_tokens=False)

#model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

model = SentenceTransformer(model_save_path)
test_evaluator = EmbeddingSimilarityEvaluator.from_input_examples(test_samples, name='sts-test')
test_evaluator(model, output_path=model_save_path)
