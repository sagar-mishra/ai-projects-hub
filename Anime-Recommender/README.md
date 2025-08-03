# Anime-Recommender System

An interactive LLM-powered Anime Recommender System assistant that uses **LangChain**, **Groq**, and the **Streamlit** framework to recommend anime — all running **locally**. 



## 📌 Project Overview

| Feature                     | Description                                             |
|---------------------------- |---------------------------------------------------------|
| 🧠 LLM                      | llama-3.1-8b-instant via [Groq](https://console.groq.com/playground)            |
| 🔗 Agent Framework          | [LangChain](https://www.langchain.com/)                 |
| 🌐 UI                       | [Streamlit](https://streamlit.io/) Web Interface        |
| 🔒 Privacy                  | 100% local — no cloud or API keys required              |

---

---

## 📁 Folder Structure
Anime-Recommender/ <br>
├── data/   
│   ├── anime_with_synopsis.csv <br>
├── app/   
│   ├── app.py # Stremlit UI <br>
├── config/  
│   ├── config.py <br>
├── logs/   
│   ├── logs.txt ...... <br>
├── pipeline/    
│   ├── build_pipeline.py # load data and create vector store pipeline <br>
│   ├── build_pipeline.py # get recommendation pipeline <br>
├── src/    
│   ├── data_loader.py # load data   <br>  
│   ├── prompt_template.py # prompt creation<br> 
│   ├── recommender.py # recommendation logic   <br> 
│   ├── vector_store.py # vectore store build and load logic<br> 
├── utils/    
│   ├── custom_exception.py  <br> 
│   ├── logger.py<br> 
├── requirements.txt <br>  
├── setup.py <br>   


## Set Up Python Environment
conda create -n langchain_env python=3.10 -y <br>
conda activate langchain_env <br>
pip install -e .<br>

## ▶️ Run the App
streamlit run app/app.py


