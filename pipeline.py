from langchain_unstructured import UnstructuredLoader
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from unstructured.cleaners.core import clean_extra_whitespace
from sentence_transformers import SentenceTransformer

from typing import List 
from unstructured.documents.elements import Element

import torch
import os
import re 

class Solution:
    def clean_word(self, w: str) -> str:
        letters = set('aáàảãạăaáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvwxyýỳỷỹỵz0123456789')
        new_w = ''
        for letter in w:
            if letter.lower() in letters or letter == '.':
                new_w += letter.lower()
        return new_w
    
    def preprocessing(self, doc:str) -> str:
        doc = doc.replace('\n', ' ').replace('==', ' ')
        words = doc.split()
        cleaned_words = [self.clean_word(word) for word in words]
        new_doc = ' '.join(cleaned_words)
        return new_doc
    

    def Pull_Data(self, folder_path: str):
        file_path = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]
    
        for file in file_path:
            docs = []
            loader_doc = UnstructuredLoader(file)
            loader_chunk = UnstructuredLoader(
                file,
                post_processors=[
                    self.remove_footer_elements,
                    clean_extra_whitespace
                ],
                chunking_strategy = "basic",
                max_characters = 500,
                include_orig_elements = False,
            )
            docs = loader_chunk.load()
            #print(f'doc = {docs}')

            embeddings = []
            for doc in docs:
                doc.page_content = self.preprocessing(doc.page_content)
                embedding = model.encode(doc.page_content)
                embeddings.append(embedding)
                #print(f'embedding = {embedding}') 


if __name__ == "__main__":
    folder_path ='Thue_document'
    solution = Solution()
    print(texts[0:10])
    print(embeddings[0:10])
    print(documents[0:10])