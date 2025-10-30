############################ SIMILARITY_SEARCH ############################
import chromadb
from chromadb.utils import embedding_functions
import torch
import re


sentence_tranformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="AITeamVN/Vietnamese_Embedding")
chromadb_client = chromadb.PersistentClient(path="vector_database")
collection = chromadb_client.get_collection(
    name="new_collection",
    embedding_function= sentence_tranformer_ef,
    )

def similarity(question):
    results = collection.query(
    query_texts= question, 
    n_results= 10,
    include=['documents','distances','metadatas'],
    )
    return results

#print(f'count= {collection.count()}')
#print(similarity(question))

############################ BM25_ALGORITHM ############################
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

def top_bm25(question):
    docs = similarity(question)["documents"][0]      # lấy list các đoạn văn
    metas = similarity(question)["metadatas"][0]     # lấy list metadata tương ứng

    documents = [
        Document(page_content=doc, metadata=meta)
        for doc, meta in zip(docs, metas)
    ]

    # Tạo BM25 retriever
    retriever = BM25Retriever.from_documents(documents)

    # Gọi truy vấn
    bm25_results = retriever.invoke(question)[:2]
    
    return bm25_results


############################ GENERATIVE_AI ############################

from transformers import AutoTokenizer, AutoModelForCausalLM
tokenizer = AutoTokenizer.from_pretrained("VietAI/gpt-neo-1.3B-vietnamese-news")
model = AutoModelForCausalLM.from_pretrained("VietAI/gpt-neo-1.3B-vietnamese-news", low_cpu_mem_usage=True, dtype=torch.float16, device_map="auto")

#device = torch.device("cuda" if torch.cuda.is_available() else "cpu") 
#model.to(device)


def gen(prompt):
    device = torch.device("cpu")
    input_ids = tokenizer(prompt, return_tensors="pt")['input_ids'].to(device)
    
    gen_tokens = model.generate(
        input_ids,
        max_new_tokens=300,  
        do_sample=True,
        temperature=0.9,
        top_k=20
    )
    return gen_tokens


def reply(question):
    top_2 = []
    for r in top_bm25(question)[0:2]:
        #print("----")
        #print(r.page_content)

        prompt = f"""Câu hỏi: {question}

            Dữ liệu: {r.page_content}

            Trả lời:"""
        
        gens = gen(prompt)
            
        gen_text = tokenizer.decode(gens[0], skip_special_tokens=True)
        top_2.append((gen_text, r.metadata))
    return top_2


#question = "quy định về thuế đối với doanh nghiệp như thế nào?"
#print(reply(question)[0][0].split("Trả lời:")[-1].strip())