import pandas as pd
import pickle
from textblob import TextBlob
import datetime
import time
import os
from nltk.tokenize import word_tokenize
import logging


#ocr_data = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\INPUT_DATA\\Cupird_Artwork_EU_Spanish_German_Ocr_Output7200000220518_English_GB.xls','rb'),sheet_name='EU_Spanish_German_Ocr_Output72')

get_column_names = []
def get_cloumn_names(df):
    for col in df.columns:
        get_column_names.append(col)

# print(ocr_data['Keyword_EnglishEU'])
# ocr_data['Keyword_GB'] = ocr_data['Keyword_GB'].str.lower()
# english_dataframe = ocr_data[['Keyword_GB','Claims_GB','Ingredients_GB','Keyword_EnglishEU']]
# english_dataframe.columns = ['Keyword', 'Context','Ingredients','Keyword_EnglishEU']
# #english_dataframe["Keyword"] = english_dataframe["Keyword"].str.lower()
# german_dataframe = ocr_data[['Keyword_GermanDach','Claims_GermanDach','IngredientsInGerman_DACH','Keyword_EnglishEU']]
# german_dataframe.columns = ['Keyword', 'Context','Ingredients','Keyword_EnglishEU']
# #german_dataframe["Keyword"] = german_dataframe["Keyword"].str.lower()
# spanish_dataframe = ocr_data[['Keyword_Spanish','Claims_Spanish','IngredientsInSpanish','Keyword_EnglishEU']]
# spanish_dataframe.columns = ['Keyword', 'Context','Ingredients','Keyword_EnglishEU']
#spanish_dataframe["Keyword"] = spanish_dataframe["Keyword"].str.lower()

# french_dataframe = ocr_data[['Keyword French','Context French','Ingredients French','Reason']]
# french_dataframe.columns = ['Keyword', 'Context','Ingredients','Reason']
# context = english_dataframe['Context'].to_list()
# keywords_ocr = english_dataframe['Keyword'].to_list()
# claim_keyword_list = ['gluten','vegetarians','milk','vegan','egg','lactose','dairy','vegetarian']

'''
Load the model
'''
# filename = 'model\\finalized_model.sav'
# loaded_model = pickle.load(open(filename, 'rb'))


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


'''
Check Dataframe
'''
def check_false_df(df):
    if df.dropna().empty:
        pass
    else:
        reason = []
        for i in range(len(df.index)):
            reason.append("No matching claim found in database")

            df['Reason'] = reason
        df = df.drop(['claim'], axis=1)

    return df

'''
Write now not in use just created the function for future use
'''
def contradict_claims_check(df):
    justify_claim_list = []
    contradict = "Contradict"
    claimlist = positive_negative_classifier(df)
    if len(claimlist) > 0:
        for claim in claimlist:
            if claim == claimlist[0]:
                justify_claim_list.append(claim)
            else:
                justify_claim_list.append(contradict)

    return justify_claim_list

'''
Check for positive and negative classification using ML model
'''
def positive_negative_classifier(df):
    filename = 'model\\finalized_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    justify_claim = []
    for sentence in df['Context']:
        result = TextBlob(sentence, classifier=loaded_model)
        justify_claim.append(result.classify())

    return justify_claim

'''
Check for contradicting claims
'''
def contradicting_claim(df):
    claim_list = positive_negative_classifier(df)
    result = False
    if len(claim_list) > 0:
        result = all(elem == claim_list[0] for elem in claim_list)
    if result:
        resultant = "No contradiction"
    else:
        resultant = "contradicting"
    return resultant

'''
Check special claim in list and return dataframe with allergen reason
'''

def special_claim_check(df,keyword,allergen):
    special_claim = df[df['justify claim'] == "special"]
    allergent_list = []
    final_allergen_list = []
    threshold = 0.80  # if needed
    for index in special_claim:
        check_list = list(special_claim[keyword][index].split(","))
        for key in allergen:
            for word in check_list:
                try:
                    # print(key)
                    # print(word)
                    res = cosdis(word2vec(word), word2vec(key))
                    # print(res)
                    # print("The cosine similarity between : {} and : {} is: {}".format(word, key, res*100))
                    if res > threshold:
                        # print("The claim is True")
                        allergent_list.append(key + ' found in ' + word)
                        print("Found a word with cosine distance > 70 : {} with original word: {}".format(word, key))
                except IndexError:
                    pass
            final_allergen_list.append(allergent_list)
    df['Reason'] = final_allergen_list
    return df


def ingredients_checklist(positive_list,ingredients):

    ingredients_list = []
    final_ingredients_list = []
    for each in positive_list:
        for ingredient in ingredients:
            if ingredient.lower().find(each.lower()) != -1:
                reason_string = each + ' found in ' + ingredient
                ingredients_list.append(reason_string)

    final_ingredients_list.append(ingredients_list)
    return final_ingredients_list


'''
Check for ingredients
'''
def ingredient_check(positive_list,ingredients):
    ingredients_list = []
    final_ingredients_list = []
    threshold = 0.90     # if needed
    for key in positive_list:
        for word in ingredients:
            try:
                # print(key)
                # print(word)
                res = cosdis(word2vec(word), word2vec(key))
                # print(res)
                #print("The cosine similarity between : {} and : {} is: {}".format(word, key, res*100))
                if res > threshold:
                   # print("The claim is True")
                    ingredients_list.append(key+' found in '+word)
                    print("Found a word with cosine distance > 80 : {} with original word: {}".format(word, key))
                else:
                    pass
            except IndexError:
                pass
    return ingredients_list

'''Compare Keywords with EU and other languages'''
def compare_english_EU_oth_lang(df):
    keyword_match = []
    for ind in df.index:
        claim_keyword = df['Keyword'][ind]
        blob = TextBlob(claim_keyword)
        claim_keyword_lang = blob.translate(to='en')
        claim_sentence = df['Keyword_EnglishEU'][ind]
        if (str(claim_sentence).lower()) ==(str(claim_keyword_lang).lower()):
            keyword_match.append("keyword match")
        else:
            keyword_match.append("keyword doesnot match")
    return keyword_match



def save_output(df,name):
    output_csv = df.to_csv('C:\\Users\\mayukhm505\\Desktop\\Unilever\\ULAFLMLCUPRID\\Artwork\\'+name+'.csv')
    return output_csv

# save_output(english_dataframe,'english')
# save_output(german_dataframe,'german')
# save_output(spanish_dataframe,'spanish')
#
# english_new_dataframe = pd.read_csv('C:\\Users\\mayukhm505\\Desktop\\Unilever\\ULAFLMLCUPRID\\Artwork\\english.csv')
# english_new_dataframe.drop(english_new_dataframe.columns[english_new_dataframe.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
# german_new_dataframe = pd.read_csv('C:\\Users\\mayukhm505\\Desktop\\Unilever\\ULAFLMLCUPRID\\Artwork\\german.csv')
# german_new_dataframe.drop(german_new_dataframe.columns[german_new_dataframe.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
# spanish_new_dataframe = pd.read_csv('C:\\Users\\mayukhm505\\Desktop\\Unilever\\ULAFLMLCUPRID\\Artwork\\spanish.csv')
# spanish_new_dataframe.drop(spanish_new_dataframe.columns[spanish_new_dataframe.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)



# header_row = 0
# german_claim = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\Allergen.xlsx','rb'),sheet_name='By Claim_Z2')
# spanish_claim = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\Allergen.xlsx','rb'),sheet_name='By Claim_ES')
# # special_claims = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\CU PIRD ALLERGEN BOT keywords_EU.xlsx','rb'),sheet_name='Exceptions')
# english_claim = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\Allergen.xlsx','rb'),sheet_name='By Claim_GB')
# #ingredients.columns = ingredients.iloc[header_row]
# #ingredients = ingredients.drop(header_row)


def claim(df):
    claim = []
    for ind in df.index:
        claim_keyword = df['Keyword'][ind]
        claim_sentence = df['Context'][ind]
        if str(claim_sentence).lower().find(str(claim_keyword).lower()) != -1:
            claim.append("true")
        else:
            claim.append("false")
    return claim

def check_rules(english_new_dataframe, english_claim, english_allergen,name):
    if english_new_dataframe.dropna().empty:
        print("The dataframe is empty")
    else:
        english = claim(english_new_dataframe)
        #print(english)
        english_new_dataframe['claim'] = english
        keyword_list = english_new_dataframe['Keyword'].to_list()
        result_keyword = []
        contradict = []
        [result_keyword.append(x) for x in keyword_list if x not in result_keyword]
        reslt_true_english_df = english_new_dataframe[english_new_dataframe['claim'] == "true"]
        reslt_false_english_df = english_new_dataframe[english_new_dataframe['claim'] == "false"]
        false_df = check_false_df(reslt_false_english_df)

        if reslt_true_english_df.dropna().empty:
            pass
        else:
            justify_claim = positive_negative_classifier(reslt_true_english_df)
            reslt_true_english_df['justify claim'] = justify_claim
            #print(justify_claim)
            english_df = reslt_true_english_df
            for key in result_keyword:
                dataframe = reslt_true_english_df[reslt_true_english_df['Keyword'] == key]
                res = contradicting_claim(dataframe)
                if res == "contradicting":
                    contradict.append(key)

            if len(contradict) > 0:
                for ind in english_df.index:
                    claim_keyword = english_df['Keyword'][ind]
                    claim_sentence = english_df['justify claim'][ind]
                    if claim_keyword in contradict:
                        justify_claim[ind] = "Contradict"

            english_df['justify claim'] = justify_claim
                # claim_data = []
                # justify_claim = []
                # for i in range(len(contradict)):
                #     justify_claim.append("Contradicting")
                #
                #
                # for con in contradict:
                #     keyword_list.remove(con)
                #
                # for key in keyword_list:
                #     claim = positive_negative_classifier(english_new_dataframe[english_new_dataframe['Keyword'] == key])
                #     claim_data.append(claim)


            print("Resultant Dataframe: ", english_df)

            english_positive_df =  english_df[english_df['justify claim'] == "positive"]
            ing_list = []
            final_list = []
            template_keywords_list = english_claim['Keywords'].tolist()
            for index in english_positive_df.index:
                ocr_keywords = english_positive_df['Keyword'][index]
                english_df_ingredients = list(english_positive_df['Ingredients'][index].split(","))
                #english_claim_ingredients = list(english_claim['Positive'][index].split(","))
                for template_keywords in template_keywords_list:
                    if ocr_keywords == template_keywords:
                        english_claim_ingredients = list(english_claim.loc[english_claim['Keywords'] == ocr_keywords, 'Positive'].iloc[0].split(","))
                        ing_list.append(ingredient_check(english_claim_ingredients, english_df_ingredients))



            #english_positive_df["Reason"] = ing_list
            print("ING LIST:",ing_list)
            if len(ing_list)>0:
                english_positive_df['Reason'] = ing_list
            else:
                english_positive_df['Reason'] = [""]
            print('Positive Dataframe: ',english_positive_df)

            english_negative_df = english_df[english_df['justify claim'] == "negative"]
            english_contradict_df = english_df[english_df['justify claim'] == "Contradict"]

            if english_negative_df.dropna().empty:
                pass
            else:
                reason_list = []
                for i in range(len(english_negative_df.index)):
                    reason_list.append(" ")
                print("Reason List: ",reason_list)
                english_negative_df['Reason'] = reason_list

            if english_contradict_df.dropna().empty:
                pass
            else:
                reason_list = []
                for i in range(len(english_contradict_df.index)):
                    reason_list.append(" Contradicting claim found")
                print("Reason List Contradict: ",reason_list)

                english_contradict_df['Reason'] = reason_list


            '''Predefined Dataframes with special case check'''
            special_list = english_df['justify claim'].tolist()
            result_check = all(elem == "special" for elem in special_list)
            if result_check:
                special_df = special_claim_check(english_df, 'Ingredients', english_allergen)
                check_df = [english_positive_df,english_negative_df,english_contradict_df,special_df,false_df]
            else:
                check_df = [english_positive_df, english_negative_df, english_contradict_df,false_df]
            df_final = []
            for df in check_df:
                if df.dropna().empty:
                    pass
                else:
                    df_final.append(df)
            new_df = pd.concat(df_final)
            print("New DF: ", new_df)
            #new_df.sort_index(axis=0, ascending=True)
            #new_df.drop(columns=['justify claim'])
            check_new_df = new_df.drop(['justify claim'], axis=1)
            check_new_df = check_new_df.drop(['claim'], axis=1)
            check_new_df = check_new_df.sort_index(axis=0, ascending=True)
            print("Headers: ",check_new_df.head())
            timestr = time.strftime("%Y%m%d-%H%M%S")
            output_csv = check_new_df.to_csv('C:\\Users\\mayukhm505\\Desktop\\Unilever\\ULAFLMLCUPRID\\Output\\'+name+'_'+timestr+'_output.csv')

    return("Check rules completed ")




# if spanish_dataframe.dropna().empty:
#     pass
# else:
#     spanish = claim(spanish_new_dataframe)
#     spanish_new_dataframe['claim'] = spanish
#     keyword_list = spanish_new_dataframe['Keyword'].to_list()
#     result_keyword = []
#     contradict = []
#     [result_keyword.append(x) for x in keyword_list if x not in result_keyword]
#     reslt_true_spanish_df = spanish_new_dataframe[spanish_new_dataframe['claim'] == "true"]
#     justify_claim = positive_negative_classifier(reslt_true_spanish_df)
#     reslt_true_spanish_df['justify claim'] = justify_claim
#     spanish_df = reslt_true_spanish_df
#     for key in result_keyword:
#         dataframe = spanish_df[spanish_df['Keyword'] == key]
#         res = contradicting_claim(dataframe)
#         if res == "contradicting":
#             contradict.append(key)
#
#     if len(contradict) > 0:
#         for ind in spanish_df.index:
#             claim_keyword = spanish_df['Keyword'][ind]
#             claim_sentence = spanish_df['justify claim'][ind]
#             if claim_keyword in contradict:
#                 justify_claim[ind] = "Contradict"
#
#     spanish_df['justify claim'] = justify_claim
#
#
#     spanish_positive_df = spanish_df[spanish_df['justify claim'] == "positive"]
#     ing_list = []
#     final_list = []
#     template_keywords_list = spanish_claim['Keywords'].tolist()
#     for index in spanish_positive_df.index:
#         ocr_keywords = spanish_positive_df['Keyword'][index]
#         spanish_df_ingredients = list(spanish_positive_df['Ingredients'][index].split(","))
#         # english_claim_ingredients = list(english_claim['Positive'][index].split(","))
#         for template_keywords in template_keywords_list:
#             if ocr_keywords == template_keywords:
#                 spanish_claim_ingredients = list(english_claim.loc[english_claim['Keywords'] == ocr_keywords, 'Positive'].iloc[0].split(","))
#                 ing_list.append(ingredient_check(spanish_claim_ingredients, spanish_df_ingredients))
#         final_list.append(ing_list)
#
#     # english_positive_df["Reason"] = ing_list
#     print("ING LIST:", final_list)
#     spanish_positive_df['Reason'] = final_list
#     print('Positive Dataframe: ', spanish_positive_df)
#
#     spanish_negative_df = spanish_df[spanish_df['justify claim'] == "negative"]
#     spanish_contradict_df = spanish_df[spanish_df['justify claim'] == "Contradict"]
#     if spanish_negative_df.dropna().empty:
#         pass
#     else:
#         reason_list = []
#         for i in range(len(spanish_negative_df.index)):
#             reason_list.append(" ")
#
#     if spanish_contradict_df.dropna().empty:
#         pass
#     else:
#         reason_list = []
#         for i in range(len(spanish_contradict_df.index)):
#             reason_list.append(" Contradicting claim found")
#
#         spanish_contradict_df['Reason'] = reason_list
#
#     '''Predefined Dataframes'''
#     special_list = spanish_df['justify claim'].tolist()
#     result_check = all(elem == "special" for elem in special_list)
#     if result_check:
#         special_df = special_claim_check(spanish_df, 'Ingredients', spanish_allergen)
#         check_df = [spanish_positive_df, spanish_negative_df, spanish_contradict_df, special_df]
#     else:
#         check_df = [spanish_positive_df, spanish_negative_df, spanish_contradict_df]
#     df_final = []
#     for df in check_df:
#         if df.dropna().empty:
#             pass
#         else:
#             df_final.append(df)
#     new_df = pd.concat(df_final)
#     check_new_df = new_df.drop(['justify claim'], axis=1)
#     output_csv = check_new_df.to_csv('C:\\Users\\mayukhm505\\Desktop\\Unilever\\ULAFLMLCUPRID\\Output\\spanish_output.csv')

# if german_dataframe.dropna().empty:
#     pass
# else:
#     german = claim(german_new_dataframe)
#     german_new_dataframe['claim'] = german
#     keyword_list = german_new_dataframe['Keyword'].to_list()
#     result_keyword = []
#     contradict = []
#     [result_keyword.append(x) for x in keyword_list if x not in result_keyword]
#     reslt_true_german_df = german_new_dataframe[german_new_dataframe['claim'] == "true"]
#     justify_claim = positive_negative_classifier(reslt_true_german_df)
#     reslt_true_german_df['justify claim'] = justify_claim
#     german_df = reslt_true_german_df
#     for key in result_keyword:
#         dataframe = german_df[german_df['Keyword'] == key]
#         res = contradicting_claim(dataframe)
#         if res == "contradicting":
#             contradict.append(key)
#
#     if len(contradict) > 0:
#         for ind in german_df.index:
#             claim_keyword = german_df['Keyword'][ind]
#             claim_sentence = german_df['justify claim'][ind]
#             if claim_keyword in contradict:
#                 justify_claim[ind] = "Contradict"
#
#     german_df['justify claim'] = justify_claim
#
#     german_positive_df = german_df[german_df['justify claim'] == "positive"]
#     ing_list = []
#     final_list = []
#     template_keywords_list = german_claim['Keywords'].tolist()
#     for index in german_positive_df.index:
#         ocr_keywords = german_positive_df['Keyword'][index]
#         spanish_df_ingredients = list(german_positive_df['Ingredients'][index].split(","))
#         # english_claim_ingredients = list(english_claim['Positive'][index].split(","))
#         for template_keywords in template_keywords_list:
#             if ocr_keywords == template_keywords:
#                 german_claim_ingredients = list(
#                     german_claim.loc[german_claim['Keywords'] == ocr_keywords, 'Positive'].iloc[0].split(","))
#                 ing_list.append(ingredient_check(german_claim_ingredients, spanish_df_ingredients))
#         final_list.append(ing_list)
#
#     # english_positive_df["Reason"] = ing_list
#     print("ING LIST:", final_list)
#     german_positive_df['Reason'] = final_list
#     print('Positive Dataframe: ', german_positive_df)
#
#     german_negative_df = german_df[german_df['justify claim'] == "negative"]
#     german_contradict_df = german_df[german_df['justify claim'] == "Contradict"]
#     if german_negative_df.dropna().empty:
#         pass
#     else:
#         reason_list = []
#         for i in range(len(german_negative_df.index)):
#             reason_list.append(" ")
#
#     if german_contradict_df.dropna().empty:
#         pass
#     else:
#         reason_list = []
#         for i in range(len(german_contradict_df.index)):
#             reason_list.append(" Contradicting claim found")
#
#         german_contradict_df['Reason'] = reason_list
#
#     '''Predefined Dataframes'''
#     special_list = german_df['justify claim'].tolist()
#     result_check = all(elem == "special" for elem in special_list)
#     if result_check:
#         special_df = special_claim_check(german_df, 'Ingredients', german_allergen)
#         check_df = [german_positive_df, german_negative_df, german_contradict_df, special_df]
#     else:
#         check_df = [german_positive_df, german_negative_df, german_contradict_df]
#     df_final = []
#     for df in check_df:
#         if df.dropna().empty:
#             pass
#         else:
#             df_final.append(df)
#     new_df = pd.concat(df_final)
#     check_new_df = new_df.drop(['justify claim'], axis=1)
#     output_csv = check_new_df.to_csv('C:\\Users\\mayukhm505\\Desktop\\Unilever\\ULAFLMLCUPRID\\Output\\german_output.csv')

# if english_dataframe.empty:
#     pass
# else:
#     english = claim(english_new_dataframe)
#     print(english)
#     english_new_dataframe['claim'] = english
#     reslt_false_english_df = english_new_dataframe[english_new_dataframe['claim'] == "false"]
#
# if spanish_dataframe.empty:
#     pass
# else:
#     spanish = claim(spanish_new_dataframe)
#     spanish_new_dataframe['claim'] = spanish
#     reslt_false_spanish_df = spanish_new_dataframe[spanish_new_dataframe['claim'] == "false"]
#
# if german_dataframe.empty:
#     pass
# else:
#     german = claim(german_new_dataframe)
#     german_new_dataframe['claim'] = german
#     reslt_false_spanish_df = german_new_dataframe[german_new_dataframe['claim'] == "false"]

def main():
    folder = 'C:\\Users\\mayukhm505\\Desktop\\Unilever\\INPUT_DATA\\'
#    logging.basicConfig(filename='Log\\error.log', encoding='utf-8', level=logging.DEBUG)
    input_folder = os.listdir('C:\\Users\\mayukhm505\\Desktop\\Unilever\\INPUT_DATA\\')
    for file in input_folder:
        ocr_data = pd.read_excel(open(folder+file,'rb'), sheet_name='EU_Spanish_German_Ocr_Output72')
        if len(ocr_data['Keyword_GB'].dropna().tolist())> 0:
            ocr_data['Keyword_GB'] = ocr_data['Keyword_GB'].str.lower()
        if len(ocr_data['Keyword_Spanish'].dropna().tolist())> 0:
            ocr_data['Keyword_Spanish'] = ocr_data['Keyword_Spanish'].str.lower()
        if len(ocr_data['Keyword_GermanDach'].dropna().tolist())> 0:
            ocr_data['Keyword_GermanDach'] = ocr_data['Keyword_GermanDach'].str.lower()

        print("Folder path:",folder+file)

        Allergen = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\Allergen.xlsx', 'rb'),sheet_name='Allergen')
        Claimable = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\Allergen.xlsx', 'rb'),sheet_name='Claim')
        english_allergen = Allergen["Allergen in Ingredent list"].dropna().tolist()
        german_allergen = Allergen["Allergen in Ingredent list German"].dropna().tolist()
        spanish_allergen = Allergen["Allergen in Ingredent list Spanish"].dropna().tolist()

        english_dataframe = ocr_data[['Keyword_GB', 'Claims_GB', 'Ingredients_GB', 'Keyword_EnglishEU']]
        english_dataframe.columns = ['Keyword', 'Context', 'Ingredients', 'Keyword_EnglishEU']
        #english_dataframe["Keyword"] = english_dataframe["Keyword"].str.lower()
        german_dataframe = ocr_data[['Keyword_GermanDach', 'Claims_GermanDach', 'IngredientsInGerman_DACH', 'Keyword_EnglishEU']]
        german_dataframe.columns = ['Keyword', 'Context', 'Ingredients', 'Keyword_EnglishEU']
        #german_dataframe["Keyword"] = german_dataframe["Keyword"].str.lower()
        spanish_dataframe = ocr_data[['Keyword_Spanish', 'Claims_Spanish', 'IngredientsInSpanish', 'Keyword_EnglishEU']]
        spanish_dataframe.columns = ['Keyword', 'Context', 'Ingredients', 'Keyword_EnglishEU']

        save_output(english_dataframe, 'english')
        save_output(german_dataframe, 'german')
        save_output(spanish_dataframe, 'spanish')

        header_row = 0
        german_claim = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\Allergen.xlsx', 'rb'),
                                     sheet_name='By Claim_Z2')
        spanish_claim = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\Allergen.xlsx', 'rb'),
                                      sheet_name='By Claim_ES')
        # special_claims = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\CU PIRD ALLERGEN BOT keywords_EU.xlsx','rb'),sheet_name='Exceptions')
        english_claim = pd.read_excel(open('C:\\Users\\mayukhm505\\Desktop\\Unilever\\Allergen.xlsx', 'rb'),
                                      sheet_name='By Claim_GB')
        if len(english_claim['Keywords'].dropna().tolist())> 0:
            english_claim['Keywords'] = english_claim['Keywords'].str.lower()
        if len(german_claim['Keywords'].dropna().tolist())> 0:
            german_claim['Keywords'] = german_claim['Keywords'].str.lower()
        if len(spanish_claim['Keywords'].dropna().tolist())> 0:
            spanish_claim['Keywords'] = spanish_claim['Keywords'].str.lower()

        # ingredients.columns = ingredients.iloc[header_row]
        # ingredients = ingredients.drop(header_row)

        english_new_dataframe = pd.read_csv('C:\\Users\\mayukhm505\\Desktop\\Unilever\\ULAFLMLCUPRID\\Artwork\\english.csv')
        english_new_dataframe.drop(english_new_dataframe.columns[english_new_dataframe.columns.str.contains('unnamed', case=False)], axis=1,inplace=True)
        german_new_dataframe = pd.read_csv('C:\\Users\\mayukhm505\\Desktop\\Unilever\\ULAFLMLCUPRID\\Artwork\\german.csv')
        german_new_dataframe.drop(german_new_dataframe.columns[german_new_dataframe.columns.str.contains('unnamed', case=False)], axis=1,inplace=True)
        spanish_new_dataframe = pd.read_csv('C:\\Users\\mayukhm505\\Desktop\\Unilever\\ULAFLMLCUPRID\\Artwork\\spanish.csv')
        spanish_new_dataframe.drop(spanish_new_dataframe.columns[spanish_new_dataframe.columns.str.contains('unnamed', case=False)], axis=1,inplace=True)

        try:
            check_rules(english_dataframe, english_claim, english_allergen, 'english')
        except:
            print("English Error Occurred")
           # logging.error('English Error Occurred')
        try:
            check_rules(german_dataframe, german_claim, german_allergen, 'german')
        except:
            print("German Error Occurred")
          #  logging.error('German Error Occurred')
        try:
            check_rules(spanish_dataframe, spanish_claim, spanish_allergen, 'spanish')
        except:
            print("Spanish Error Occurred")
           # logging.error('Spanish Error Occurred')



if __name__ == "__main__":
    main()

