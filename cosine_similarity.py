import pandas as pd
def word2vec(word):
    from collections import Counter
    from math import sqrt

    # count the characters in word
    cw = Counter(word)
    # precomputes a set of the different characters
    sw = set(cw)
    # precomputes the "length" of the word vector
    lw = sqrt(sum(c*c for c in cw.values()))

    # return a tuple
    return cw, sw, lw

def cosdis(v1, v2):
    # which characters are common to the two words?
    common = v1[1].intersection(v2[1])
    # by definition of cosine distance we have
    return sum(v1[0][ch]*v2[0][ch] for ch in common)/v1[2]/v2[2]


header_row = 0
ingredients = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\CU PIRD ALLERGEN BOT keywords_EU.xlsx','rb'),sheet_name='BY ALLERGEN_ALL LANGUAGES')
ocr_data = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\CupirdArtworkOCR.xls','rb'),sheet_name='Sheet1')
context = ocr_data['Context'].to_list()
ingredients.columns = ingredients.iloc[header_row]
#ingredients = ingredients.drop(header_row)
ingredients_list = ingredients["Allergen in Ingredent list "].dropna().tolist()
del ingredients_list[0]

str = " Water, rapeseed oil, sour cream (8%) (MILK), spirit vinegar, modified starch, EGG yolk, yoghurt powder (MILK), salt, sugar, acid (lactic acid), chives (0.15%), onion powder, thickener (xanthan gum), black pepper."
check_list = list(str.split(","))

threshold = 0.70     # if needed
for key in ingredients_list:
    for word in check_list:
        try:
            # print(key)
            # print(word)
            res = cosdis(word2vec(word), word2vec(key))
            # print(res)
            #print("The cosine similarity between : {} and : {} is: {}".format(word, key, res*100))
            if res > threshold:
                print("Found a word with cosine distance > 70 : {} with original word: {}".format(word, key))
        except IndexError:
            pass