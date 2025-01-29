# speech-finetuning

This repository contains Python code to process political speech data for fine-tuning the language models analyzed in Aligned Foresight's [Candidate Speech Analysis](https://alignedforesight.substack.com/p/were-the-debates-scripted-411) projects.


## Quickstart
The data processing pipeline uses Python 3.12, and relies on spaCy's `en_core_web_trf` model. To install the necessary dependencies, run the following commands:

```commandline
python3.12 -m venv env
source env/bin/activate
pip install uv
uv pip compile requirements.in > requirements.txt 
uv pip install -r requirements.txt
python -m spacy download en_core_web_trf       
```

## Downloading and Processing Raw Data
### Candidate Finetune
For the [candidate finetune](https://alignedforesight.substack.com/p/were-the-debates-scripted-411) project, raw data is already downloaded and available in `data/raw`.

The data can be processed by running:
```commandline
python main.py --dataset harris --output_file harris.csv
python main.py --dataset trump --output_file trump.csv
python main.py --dataset debate --output_file debate.csv
python main.py --dataset vance --output_file vance.csv
python main.py --dataset walz --output_file walz.csv
python main.py --dataset vice_debate --output_file vice_debate.csv
```

For the [trump finetune](https://alignedforesight.substack.com/p/what-trumps-speeches-reveal-about) project, raw data can be downloaded and processed using the DATA-get-speeches.ipynb notebook:
```commandline
jupyter notebook DATA-get-speeches.ipynb
```

## Downloading Processed Data
All the processed data for the projects can be found in their dedicated Drive folders:
* [Candidate Finetune](https://drive.google.com/drive/u/0/folders/1kdfqLb0C0Yg9TA-lEnwwA38_pY1Vs8SU)
* [Trump Finetune](https://drive.google.com/drive/u/0/folders/1_ifNoJxvgUe9oiY8b-HJFph02yftMol5)