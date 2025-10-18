"""
This is uses langchain for splitting large documents into chunks using a chunk overlap of 100 characters by default @Y22CS191 Vemuri Sasi Vardhan

"""


from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class documentSplitter:
    def __init__(self):
        print("Object Created")
    
    def chunkDoc(self,path):
        self.path=path
        loader=PyPDFLoader(self.path)
        doc=loader.load()

        fulltext="\n".join([d.page_content for d in doc])

        paras=fulltext.split("\n\n")\
        
        #for parsing large Chunks lets uswe recursive text splitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)

        chunks=[]

        for para in paras:
            chunks.extend(splitter.split_text(para.strip()))
        return chunks

