# WIP!!


# IMPORTANT - Read Before Using

Whether this works or not may depend on your computer. I use a mac, and had to use enviroment_mac.yml instead of environment.yml. To test FinBERT, follow the instructions in the readme within the FinBERT directory. HOWEVER, I have already downloaded the model and placed it in the directory models/sentiment/LLM_model. I have also already placed the config.json file there. This config file is modified from the original, and to work n our material it might require slight modifications again, but will evaluate once implemented.

# ERRORS

I had to modify the environment file and the config file in the models directory to get the test to work. Many of the issues I ran into stem from macOS no longer supporting certain dependencies, so it might require some testing with different systems. 

# To Run

To test the provided test.txt file in the directory, I first ran the environment script as described in the FinBERT readme, and then I ran:
~~~
finBERT % export PYTHONPATH=$(pwd)
python -m scripts.predict \
  --text_path test.txt \
  --output_dir output \
  --model_path models/sentiment/LLM_model
~~~
This should output results to the output directory (there are probably some hter rom my first test) which is a csv with the senitment scores for particular sections of the text. Let me know if there are any issues.
