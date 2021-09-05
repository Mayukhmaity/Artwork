import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab)

ocr_data = pd.read_excel(open('/Users/macbook/PycharmProjects/Artwork/Input/CupirdArtworkOCR.xls','rb'),sheet_name='Sheet1')
get_column_names = []
for col in ocr_data.columns:
    get_column_names.append(col)

english_dataframe = ocr_data[['Keyword','Context','Ingredients']]
german_dataframe = ocr_data[['Keyword German','Context German','Ingredients German']]
german_dataframe.columns = ['Keyword', 'Context','Ingredients']
spanish_dataframe = ocr_data[['Keyword Spanish','Context Spanish','Ingredients Spanish']]
spanish_dataframe.columns = ['Keyword', 'Context','Ingredients']
# french_dataframe = ocr_data[['Keyword French','Context French','Ingredients French']]
# french_dataframe.columns = ['Keyword', 'Context','Ingredients']

german_claim = pd.read_excel(open('/Users/macbook/PycharmProjects/Artwork/Input/CU PIRD ALLERGEN BOT keywords_EU.xlsx','rb'),sheet_name='By Claim_Z2')
spanish_claim = pd.read_excel(open('/Users/macbook/PycharmProjects/Artwork/Input/CU PIRD ALLERGEN BOT keywords_EU.xlsx','rb'),sheet_name='By Claim_ES')
special_claims = pd.read_excel(open('/Users/macbook/PycharmProjects/Artwork/Input/CU PIRD ALLERGEN BOT keywords_EU.xlsx','rb'),sheet_name='Exceptions')
english_claim = pd.read_excel(open('/Users/macbook/PycharmProjects/Artwork/Input/CU PIRD ALLERGEN BOT keywords_EU.xlsx','rb'),sheet_name='Claim')
#ingredients.columns = ingredients.iloc[header_row]
#ingredients = ingredients.drop(header_row)
german_claim_positive = german_claim["Positive"].dropna().tolist()
spanish_claim_positive = spanish_claim["Positive"].dropna().tolist()
english_claim_positive = english_claim["Positive"].dropna().tolist()
german_claim_negative = german_claim["Negative"].dropna().tolist()
spanish_claim_negative = spanish_claim["Negative"].dropna().tolist()
english_claim_negative = english_claim["Negative"].dropna().tolist()
context = english_dataframe['Context'].to_list()
keywords_ocr = english_dataframe['Keyword'].to_list()
claim_keyword_list = ['gluten','vegetarians','milk','vegan','egg','lactose','dairy','vegetarian']


def save_output(df,name):
    output_csv = df.to_csv('/Users/macbook/PycharmProjects/Artwork/Middleware/'+name+'.csv')
    return output_csv

save_output(english_dataframe,'english')
print("***** First English Output Data *****")
save_output(german_dataframe,'german')
print("***** First German Output Data *****")
save_output(spanish_dataframe,'spanish')
print("***** First Spanish Output Data *****")

english_new_dataframe = pd.read_csv('/Users/macbook/PycharmProjects/Artwork/Middleware/english.csv')
english_new_dataframe.drop(english_new_dataframe.columns[english_new_dataframe.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)

german_new_dataframe = pd.read_csv('/Users/macbook/PycharmProjects/Artwork/Middleware/german.csv')
german_new_dataframe.drop(german_new_dataframe.columns[german_new_dataframe.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)

spanish_new_dataframe = pd.read_csv('/Users/macbook/PycharmProjects/Artwork/Middleware/spanish.csv')
spanish_new_dataframe.drop(spanish_new_dataframe.columns[spanish_new_dataframe.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)

'''
Rule 1 to check the context with keywords and then again check the context with the postive claim keywords
and negative claim keywords if it matches then it is either positive or negative claim
'''
def claim(df):
    claim = []
    for ind in ocr_data.index:
        claim_keyword = df['Keyword'][ind]
        claim_sentence = df['Context'][ind]
        if str(claim_sentence).lower().find(str(claim_keyword).lower()) != -1:
            claim.append("true")
        else:
            claim.append("false")
    return claim

if english_dataframe.dropna().empty:
    print("Sorry the file is empty for English")
else:
    english = claim(english_new_dataframe)
    justify_claim = []
    #print(english)
    english_new_dataframe['claim'] = english
    reslt_true_english_df = english_new_dataframe[english_new_dataframe['claim'] == "true"]
    save_output(reslt_true_english_df, 'english')
    '''
    Check the Context is a positive claim or negative claim 
    '''
    english_claim_dataframe = pd.read_csv('/Users/macbook/PycharmProjects/Artwork/Middleware/english.csv')
    english_claim_dataframe.drop(english_claim_dataframe.columns[english_claim_dataframe.columns.str.contains('unnamed', case=False)], axis=1,inplace=True)
    patterns = [nlp.make_doc(text) for text in english_claim_positive]
    matcher.add("TerminologyList", patterns)
    for sentence in english_claim_dataframe['Context']:
        doc = nlp(sentence)
        matches = matcher(doc)
        if len(matches) > 0:
            justify_claim.append("positive claim")
        else:
            justify_claim.append("check negative claim")
        for match_id, start, end in matches:
            span = doc[start:end]
           # print(span.text)
   # print(justify_claim)
    justify_negative_claim = []
    english_claim_dataframe['justify claim'] = justify_claim
    reslt_negative_english_df = english_claim_dataframe[english_claim_dataframe['justify claim'] == "check negative claim"]
    patterns = [nlp.make_doc(text) for text in english_claim_negative]
    matcher.add("TerminologyList", patterns)
    for sentence in reslt_negative_english_df['Context']:
        doc = nlp(sentence)
        matches = matcher(doc)
        if len(matches) > 0:
            justify_negative_claim.append("negative claim")
        else:
            justify_negative_claim.append("no claim found")
        for match_id, start, end in matches:
            span = doc[start:end]
            #print(span.text)
    reslt_negative_english_df['justify claim'] = justify_negative_claim
    claim_output_df = pd.concat([english_claim_dataframe[english_claim_dataframe['justify claim'] == "positive claim"],reslt_negative_english_df])
    save_output(claim_output_df, 'english')

if spanish_dataframe.dropna().empty:
    print("Sorry the file is empty for Spanish")
else:
    spanish = claim(spanish_new_dataframe)
    justify_claim = []
    spanish_new_dataframe['claim'] = spanish
    reslt_true_spanish_df = spanish_new_dataframe[spanish_new_dataframe['claim'] == "true"]
    save_output(reslt_true_spanish_df, 'english')
    spanish_claim_dataframe = pd.read_csv('/Users/macbook/PycharmProjects/Artwork/Middleware/spanish.csv')
    patterns = [nlp.make_doc(text) for text in spanish_claim_positive]
    matcher.add("TerminologyList", patterns)
    for sentence in spanish_claim_dataframe['Context']:
        doc = nlp(sentence)
        matches = matcher(doc)
        if len(matches) > 0:
            justify_claim.append("claim")
        else:
            justify_claim.append("no claim")
        for match_id, start, end in matches:
            span = doc[start:end]
            print(span.text)
    spanish_claim_dataframe['justify claim'] = justify_claim
    save_output(spanish_claim_dataframe, 'spanish')

if german_dataframe.dropna().empty:
    print("Sorry the file is empty for German")
else:
    german = claim(german_new_dataframe)
    justify_claim = []
    german_new_dataframe['claim'] = german
    reslt_true_german_df = german_new_dataframe[german_new_dataframe['claim'] == "true"]
    save_output(reslt_true_german_df, 'english')
    german_claim_dataframe = pd.read_csv('/Users/macbook/PycharmProjects/Artwork/Middleware/spanish.csv')
    patterns = [nlp.make_doc(text) for text in german_claim_positive]
    matcher.add("TerminologyList", patterns)
    for sentence in german_claim_dataframe['Context']:
        doc = nlp(sentence)
        matches = matcher(doc)
        if len(matches) > 0:
            justify_claim.append("claim")
        else:
            justify_claim.append("no claim")
        for match_id, start, end in matches:
            span = doc[start:end]
            print(span.text)
    print(justify_claim)
    german_claim_dataframe['justify claim'] = justify_claim
    save_output(german_claim_dataframe, 'german')

if english_dataframe.dropna().empty:
    pass
else:
    english = claim(english_new_dataframe)
    print(english)
    english_new_dataframe['claim'] = english
    reslt_false_english_df = english_new_dataframe[english_new_dataframe['claim'] == "false"]

if spanish_dataframe.dropna().empty:
    pass
else:
    spanish = claim(spanish_new_dataframe)
    spanish_new_dataframe['claim'] = spanish
    reslt_false_spanish_df = spanish_new_dataframe[spanish_new_dataframe['claim'] == "false"]

if german_dataframe.dropna().empty:
    pass
else:
    german = claim(german_new_dataframe)
    german_new_dataframe['claim'] = german
    reslt_false_spanish_df = german_new_dataframe[german_new_dataframe['claim'] == "false"]


'''
Rule 2: if the claim is positive then check the ingredients from the Allergen ingredients list 
and define it in the Reason column about the  allergen ingredients present in the product
'''
header_row = 0
english_check_claim_dataframe = pd.read_csv('/Users/macbook/PycharmProjects/Artwork/Middleware/english.csv')
ingredients = pd.read_excel(open('/Users/macbook/PycharmProjects/Artwork/Input/CU PIRD ALLERGEN BOT keywords_EU.xlsx','rb'),sheet_name='BY ALLERGEN_ALL LANGUAGES')
ingredients.columns = ingredients.iloc[header_row]
#ingredients = ingredients.drop(header_row)
ingredients_list = ingredients["Allergen in Ingredent list "].dropna().tolist()
del ingredients_list[0]
print(ingredients_list)

#print(english)
#english_dataframe['claim'] = claim
#reslt_english_df = english_dataframe[english_dataframe['claim'] == "true"]

#english_dataframe = ocr_data[['Keyword','Context','Ingredients','Reason','claim']]

#output_excel  = english_dataframe.to_csv('C:\\Users\\mayukhm505\\Desktop\\Unilever\\CupirdArtworkFinalOCR.csv')

#output_excel = ocr_data.to_csv('C:\\Users\\mayukhm505\\Desktop\\Unilever\\CupirdArtworkFinalOCR.csv')
#print(claim)



# def word2vec(word):
#     from collections import Counter
#     from math import sqrt
#
#     # count the characters in word
#     cw = Counter(word)
#     # precomputes a set of the different characters
#     sw = set(cw)
#     # precomputes the "length" of the word vector
#     lw = sqrt(sum(c*c for c in cw.values()))
#
#     # return a tuple
#     return cw, sw, lw
#
# def cosdis(v1, v2):
#     # which characters are common to the two words?
#     common = v1[1].intersection(v2[1])
#     # by definition of cosine distance we have
#     return sum(v1[0][ch]*v2[0][ch] for ch in common)/v1[2]/v2[2]
#
#
# header_row = 0
#
#
# print(english_claim_positive)
#
# str = "Water, rapeseed oil, sour cream (8%) (MILK), spirit vinegar, modified starch, EGG yolk, yoghurt powder (MILK), salt, sugar, acid (lactic acid), chives (0.15%), onion powder, thickener (xanthan gum), black pepper."
# check_list = list(str.split(","))
# threshold = 0.80     # if needed
# for key in english_claim_positive:
#     for word in check_list:
#         try:
#             # print(key)
#             # print(word)
#             res = cosdis(word2vec(word), word2vec(key))
#             # print(res)
#             #print("The cosine similarity between : {} and : {} is: {}".format(word, key, res*100))
#             if res > threshold:
#                 check_positive = "true"
#                # print("The claim is True")
#                 print("Found a word with cosine distance > 70 : {} with original word: {}".format(word, key))
#             else:
#                 check_positive = ""
#         except IndexError:
#             pass
#             if(check_positive == ""):
#                 threshold = 0.70     # if needed
#                 for key in english_claim_negative:
#                     for word in check_list:
#                         try:
#                             # print(key)
#                             # print(word)
#                             res = cosdis(word2vec(word), word2vec(key))
#                             # print(res)
#                             #print("The cosine similarity between : {} and : {} is: {}".format(word, key, res*100))
#                             if res > threshold:
#                                 pass
#                                # print("The claim is False")
#                                 print("Found a word with cosine distance > 70 : {} with original word: {}".format(word, key))
#                         except IndexError:
#                             pass