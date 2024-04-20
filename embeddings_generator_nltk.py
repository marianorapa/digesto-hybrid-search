import os

from sentence_transformers import SentenceTransformer
from langchain.text_splitter import NLTKTextSplitter
from nltk.tokenize import sent_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from langchain.text_splitter import SpacyTextSplitter
import nltk

nltk.download('punkt')
es_tokenizer = nltk.data.load("tokenizers/punkt/spanish.pickle")
import re

model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')

def create_embeddings(sections):
    return model.encode(sections)

text = """

Universidad Nacional de Luján 
  República Argentina 
CORRESP. ACTUACION Nº 803/01 - DB
LUJAN, 17 DE JULIO DE 2003
 
VISTO: La propuesta de designación de personal docente 
con carácter interino presentada por el Departamento de 
Ciencias Básicas, y 
 
CONSIDERANDO: 
La Disposición Nº 038/02 del señor Presidente del 
Consejo Directivo Departamental de Ciencias Básicas. 
Que corresponde emitir acto resolutivo conforme el 
Artículo 
13 
de 
la 
Ley 
Nacional 
de 
Procedimientos 
Administrativos. 
 
Por ello, en uso de las atribuciones conferidas por 
Resolución C.S.Nº 004/86. 
 
LA PRESIDENTA DEL H. CONSEJO SUPERIOR DE LA 
UNIVERSIDAD NACIONAL DE LUJAN 
RESUELVE: 
 
ARTICULO 1º.- Designar con carácter interino al Analista de 
Sistemas Pablo César CHALE (D.N.I.Nº 27.851.739 - Legajo Nº 
2319) en un cargo de Ayudante de Primera “ad honorem”, en el 
Departamento de Ciencias Básicas, a partir del día de la 
fecha de firma del acta de puesta en funciones respectiva y 
hasta el 31 de diciembre de 2002.- 
ARTICULO 2º.- Dejar sin efecto la designación del Analista 
de Sistemas Pablo César CHALE (D.N.I.Nº 27.851.739 - Legajo 
Nº 2319) en un cargo ordinario de Ayudante de Segunda “ad 
honorem”, en el Departamento de Ciencias Básicas, a partir 
del 5 de mayo de 2002.- 
ARTICULO 3º.- Regístrese, comuníquese y archívese.- 
 
RESOLUCION P.C.S.Nº 259/03 
 
Lic. María Ester Urrutia 
Secretaria Académica 
     Lic. AMALIA TESTA 
Presidenta  
H. Consejo Superior 
 
El texto de los documentos publicados en el sitio Web de la Universidad Nacional de Luján 
no tendrá validez para su presentación en terceras instituciones y/o entidades, salvo que 
contaren con autenticación expedida por la Dirección de Despacho General.

""" # your text
text = re.sub(r'\s+', ' ', text)

print('---------------')
print("NLTKTextSplitter.split_text")
text_splitter = NLTKTextSplitter()
docs = text_splitter.split_text(text)
text_splitter_sent = []
for line in docs[0].split("\n\n"):
    text_splitter_sent.append(line)

print(text_splitter_sent)
print('---------------')
print("es_tokenizer.tokenize")
sentences = es_tokenizer.tokenize(text)
print(sentences)


print('---------------')
print("PunktSentenceTokenizer.tokenize")
punkt_param = PunktParameters()
punkt_param.sent_starters = ['VISTO:', 'CONSIDERANDO:']
sentence_splitter = PunktSentenceTokenizer(punkt_param)
sentences = sentence_splitter.tokenize(text)
print(sentences)

print('---------------')
print("SpaCyTextSplitter.split_text")
text_splitter = SpacyTextSplitter()
docs = text_splitter.split_text(text)
print(docs)

# file_path = '../raw-digest/RES_PHCS_NÂº_259_03.pdf.txt'
#
# with open(file_path, 'r') as f:
#     text = f.read()
#     embeddings = create_embeddings(text)
#
# with open(file_path + '-embeddings.txt', 'w') as f:
#     f.write(str(embeddings))