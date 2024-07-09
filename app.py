import streamlit as st
from txtai.pipeline import Summary
from pypdf import PdfReader
from transformers import pipeline
from bs4 import BeautifulSoup
import requests

st.set_page_config(layout='wide')
summerizer=pipeline('summarization',model='facebook/bart-large-cnn')
@st.cache_resource
def summery_text(text):
    summary=Summary()
    text=(text)
    result=summary(text)
    return result

#Extract text from the pdf file  using pypdf
def extract_text_frmpdf(file_path):
    with open(file_path,'rb') as f:
        reader=PdfReader(f)
        page=reader.pages[0]
        text=page.extract_text(page)
    return text

#clean content
def clean_content(article):
    article=article.replace('.','.<eos>')
    article=article.replace('!','!<eos>')
    article=article.replace('?','?<eos>')
    sentences=article.split('<eos>')
    max_chunk=500
    current_chunk=0
    chunk=[]
    for sentence in sentences:
        if len(chunk)== current_chunk+1:
            if len(chunk[current_chunk])+len(sentence.split(' ')) <= max_chunk:
                chunk[current_chunk].extend(sentence.split(' '))
            else:
                current_chunk+= 1
                chunk.append(sentence.split(' '))
        else:
            print(current_chunk)
            chunk.append(sentence.split(' '))
        return chunk
#Extract content of website using huggingface
def xtract_text_frmweb(url):
    
    r=requests.get(url)
    soup=BeautifulSoup(r.text,'html.parser')
    results=soup.find_all(['h1','p'])
    text=[result.text for result in results]
    article=' '.join(text)
    chunk=clean_content(article)
    print(chunk)
    
    for chunk_id in range(len(chunk)):
        chunk[chunk_id]=' '.join(chunk[chunk_id])
    res=summerizer(chunk,max_length=80,min_length=30,do_sample=False)
    summerised_text=' '.join([summ['summary_text']for summ in res])
    print(summerised_text)
    return summerised_text

    
choice=st.sidebar.selectbox('Select your choice',['Summerize text','Summerize document','Summerize website content'])
if choice=='Summerize text':
    st.subheader('Summerize text using txtai')
    input_text=st.text_area('Enter your text here')
    if st.button('Summerize text'):
        col1,col2= st.columns([1,1])
        with col1:
            st.markdown("**Your Input Text**")
            st.info(input_text)
        with col2:
            result=summery_text(input_text)
            st.markdown('**Summerize text**')
            st.success(result)
        
elif choice=='Summerize document':
    st.subheader('Summerize documentt using txtai')
    input_file=st.file_uploader('Upload your document', type=['pdf','txt'])
    if input_file is not None: 
        if st.button('Summerize Document'):
            with open('doc_file.pdf','wb') as f:
                f.write(input_file.getbuffer())
            col1,col2= st.columns([1,1])
            with col1:
                st.markdown("**xtract text from document**")
                extracted_text=extract_text_frmpdf()
                st.info(extracted_text)
            with col2:
                result=extract_text_frmpdf('doc_file.pdf')
                st.markdown('**Summerize Document**')
                result=summery_text(result)
                st.success(result)

elif choice=='Summerize website content':
    st.subheader('Summerize website content')
    url=st.text_input('Enter your web url here')
    if not url.startswith("https"):
        #st.stop()
        pass
        
    else:
        if st.button('Summerize text'):
            col1,col2= st.columns([1,1])  
            with col1:
                st.markdown('**summerize content from website**') 
                #extracted_web_cont=xtract_text_frmweb()
                #st.info(extracted_web_cont)    
            with col2:
                res=xtract_text_frmweb(url)
                st.markdown('**Summerized Content**')
                st.success(res)
        