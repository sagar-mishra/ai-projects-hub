# Anime-Recommender System

An interactive AI-powered Anime Recommender System assistant that uses **LangChain**, **Groq**, and the **Streamlit** framework to recommend anime — all running **locally**. 



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
├── data/ <br>     
│   ├── anime_with_synopsis.csv <br>
├── app/ <br>     
│   ├── app.py # Stremlit UI <br>     
├── config/ <br>     
│   ├── config.py <br>   
├── logs/ <br>     
│   ├── logs.txt ...... <br>   
├── pipeline/ <br>     
│   ├── build_pipeline.py # load data and create vector store pipeline<br>   
│   ├── build_pipeline.py # get recommendation pipeline<br>
├── src/ <br>     
│   ├── data_loader.py # load data <br>   
│   ├── prompt_template.py # prompt creation<br>
│   ├── recommender.py # recommendation logic <br>   
│   ├── vector_store.py # vectore store build and load logic<br>
├── utils/ <br>     
│   ├── custom_exception.py<br>   
│   ├── logger.py<br>
├── requirements.txt <br>   
├── setup.py <br>   


## Set Up Python Environment
conda create -n langchain_env python=3.10 -y <br>
conda activate langchain_env <br>
pip install -e .<br>

## ▶️ Run the App
streamlit run app/app.py


