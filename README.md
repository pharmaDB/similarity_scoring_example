# Similarity Scoring

This repository includes scripts for finding the most relevant patent claim for a drug label using both the en_core_sci_lg and en_core_sci_scibert.  It is noted that en_core_sci_scibert has performance that is marginally better in testing by the authors of scispaCy.  See https://allenai.github.io/scispacy/.  In the example case, the drug Nitric Oxide under the brand Inomax is used.

```
Active Ingredient: NITRIC OXIDE
DF;Route: GAS;INHALATION
Trade_Name: INOMAX
Applicant: MALLINCKRODT HOSP
Strength: 800PPM
Appl_Type: N
Appl_No: 020845   <=== NDA number
Product_No:003
TE_CODE: AA
Approval_Date:Dec 23, 1999
RLD: Yes
RS: Yes
Type: RX
Applicant_Full_Name: MALLINCKRODT HOSP PRODUCTS IP LTD
```


From the Orange Book, we know that Inomax is related to three patents: US8431163, US8282966, and US8293284.


## Install
Python 3 is required.  `pip` or `pipenv` may be used.  The instructions below are for a system with `pip`, but `pipenv` may replace all `pip` calls and `pipenv run python` may replace all `python` calls.

```
git clone https://github.com/pharmaDB/similarity_scoring_example.git
cd similarity_scoring_example
pip install -r requirements.txt

curl -OJ https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_lg-0.4.0.tar.gz
curl -OJ https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_scibert-0.4.0.tar.gz

tar -xf en_core_sci_lg-0.4.0.tar.gz
tar -xf en_core_sci_scibert-0.4.0.tar.gz
```


## Run
```
python run_nlp.py
```


## Test
```
python -m unittest
```
