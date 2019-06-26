#Work on Children's Spellchecker

## phonetics.ipynb
This notebook contains most of the work focused on in the paper.

Several libraries will need to be installed including: pandas, textblob, stringdist, numpy, pyphonetics, sklearn, and tqdm

The first block contains all the imports required to run everything in the notebook and from their the rest of the notebook can be ran in order.

Under the metaphones section the mphone(word) function returns a phonetic representation of a given word
```
    mphone('tuchdone') #returns 'T1DN'
```
The metaphone_suggestions(word, count) function returns a list of suggestions, up to size count. The dictionary must be built before using this.
```
    metaphone_suggestions('tuchdone', 5) #returns [touchdown, touchdowns, techno, tendon, trodden]
```
## machine_translation.ipynb, different_embeddings.ipynb, weiss_deep_spell.ipynb
These notebooks contain other attempted methods for this project

## data
The data folder contains much of the data needed by the notebooks to run. 
