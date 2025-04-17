# SoundScribe

## Tagging Folder.
book_nlp_s3.py 
- This file runs the models that produce the speaker tagging. It takes the .txt file as an argument. It is loaded on an AWS EC2 to interact with AWS S3 buckets.
- Tagging accuracy is claimed to be around 90%, though is likely closer to 75% on real book data. 

lambda.py
- The lambda function activates when new data in put into the raw-data bucket S3. It takes the associated .txt file and then calls the book_nlp_s3.py file

book_nlp.py
- Same as book_nlp_s3.py but disconnected from AWS. Able to run locally. 



## Authors
Adam Rustad
Trevor Larsen
Spencer Marshall
Chase Zundel
