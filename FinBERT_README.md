# WIP!!

Currently the file is too big to add to github, looking at solutions.


# IMPORTANT - Read Before Using

Whether this works or not may depend on your computer. I use a mac, and had to use enviroment_mac.yml instead of environment.yml. To test FinBERT, follow the instructions in the readme within the FinBERT directory. HOWEVER, I have already downloaded the model and placed it in the directory models/sentiment/LLM_model. I have also already placed the config.json file there.

# ERRORS

I had to modify the environment file and the config file in the models directory to get the test to work. Many of the issues I ran into stem from macOS no longer supporting certain dependencies, so it might require some testing with different systems. To test, I ran:
~~~
finBERT % export PYTHONPATH=$(pwd)
python -m scripts.predict \
  --text_path test.txt \
  --output_dir output \
  --model_path models/sentiment/LLM_model
~~~
