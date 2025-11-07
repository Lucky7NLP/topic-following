# 🧠 Topic-Following

Our **Topic-Following** project follows the "CantTalkAboutThis: Aligning Language Models to Stay on Topic in Dialogues" paper.
This project was developed for the **NLP/DL course**.
This repository consists of an app for distractor creation upon the original dataset, and several files that include our annotation process as a group, along with the quality control we performed in 20 distinct scenarios randomly sampled from the other group's annotation pool.

---

## 🧩 Current Directory Structure

```
topic-following/
│
├── app/
│ └── app.py # Streamlit interface
│
│── dataset/ # OUR WORK
│ └── final/ # Contains csv's with our group's distractors
│ └── group7_combined_data.csv # Quality control on the other group's distractors
│
├── documents/ # Contains personal notes & meeting notes
│
├── src/
│ └── get_csv.py # Script to download or generate CSV domain data
│ └── utils.py
│
├── data/ # Csv files from ORIGINAL dataset
│ ├── real_estate.csv # Domain dataset
│ ├── insurance.csv
│ ├── travel.csv
│ └── distractors/ # Folder where new distractor csvs are saved
│
├── requirements.txt
└── README.md
```

## 🛠️ Setup Instructions (for the app)

**a. Install dependencies**  
Install all required Python packages using:
```bash
pip install -r requirements.txt
```

**b. Generate the domain-specific datasets by running**
```bash
python src/get_csv.py
```

**c. Start the web interface with**
```bash
streamlit run app/app.py
```
This command will open a new browser tab with the app interface.


**d. Create distractors**
```
In the browser tab, load a domain CSV (e.g., insurance.csv).
Click “Random Scenario” to view a random example or "Load by Index" to select in order (index starts from 0)
Review the domain, scenario, system instruction, and conversation.
Type your distractor in the provided text box.
Type the target instruction you want to violated in the next.
Press “💾 Save Distractor” to save it.
```

**e. Save results**
Each saved distractor is appended as a new row in:
```bash
data/distractors/<domain>.csv
```