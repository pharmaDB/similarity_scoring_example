import scispacy
import spacy
from load_file import read_label, read_patent, read_patent_no_dependency
from collections import OrderedDict
import copy

# load scispaCy models
en_core_sci_lg_nlp = spacy.load(
    "en_core_sci_lg-0.4.0/en_core_sci_lg/en_core_sci_lg-0.4.0")
# removing bert for the time being; this pretrained model is very slow.
# en_core_sci_scibert_nlp = spacy.load(
#     "en_core_sci_scibert-0.4.0/en_core_sci_scibert/en_core_sci_scibert-0.4.0/")

# cache for nlp object each consisting of [string, nlp_object]
string_nlp_list1 = [""] * 2
string_nlp_list2 = [""] * 2

# set number of processes for nlp.pipe
N_PROCESS = 3


def get_similarity(string1, string2, method):
    '''
    Return a semantic similarity estimate using cosine over vectors using
    the model selected by spaCy.

    Parameters:
        string1, string2 (string): two strings for comparison
        method (object): the model loaded by spaCy.load()
    '''
    global string_nlp_list1, string_nlp_list2
    if string1 == string_nlp_list1[0]:
        doc1 = string_nlp_list1[1]
    else:
        doc1 = method(string1)
        string_nlp_list1 = [string1, doc1]
    if string2 == string_nlp_list2[0]:
        doc2 = string_nlp_list2[1]
    else:
        doc2 = method(string2)
        string_nlp_list2 = [string2, doc2]
    return doc1.similarity(doc2)


def str_to_nlp(string, method):
    '''
    Return an spaCy Doc object, given an input string and a nlp method

    Parameters:
        string (string): string to be converted to a spaCy Doc object
        method (object): the nlp model loaded by spaCy.load()
    '''
    return method(string)


def get_values_from_od_of_od(od):
    '''
    Returns a list of all values [value1, value2] from {key1: {key2: [value1,
    value2, ...], ..}, ...} in order

    Parameters:
        od (OrderedDict): example: {key1:{key2:[value1,value2,...],...},...}

    '''
    return_list = []
    for key1 in od.keys():
        for key2, value in od[key1].items():
            return_list.extend(value)
    return return_list


def set_values_for_od_of_od(od, values):
    '''
    Replaces all values in OrderedDict od, of form {key1: {key2: [value1,
    value2, ...], ..}, ...}, passed by reference, with values in list values.

    Given the examples in parameters below, od becomes {key1:{key2:[value5,
    value6,...], ...}, ...}

    Parameters:
        od (OrderedDict): example: {key1:{key2:[value1,value2,...],...},...}
        values (list): example: [value5,value6,...]
    '''
    for key1 in od.keys():
        for key2 in od[key1].keys():
            for i in range(len(od[key1][key2])):
                od[key1][key2][i] = values.pop(0)
    return od


def label_section_to_patent_claim_similarity(label_sections_od,
                                             patent_no_dependency_od, nlp):
    '''
    Returns OrderedDict of {section_title:[(patent_num, claim_num,
    similarity_score),...],...}, for a single label, wherein each (patent_num,
    claim_num, similarity_score) for a label section, as defined by
    section_title, is sorted from the most similar to most dissimilar claim.

    Parameters:
        label_sections_od (OrderedDict):
                {section_title:section_text,...} for a single label from a drug
                with an NDA number
        patent_no_dependency_od (OrderedDict):
                {patent_num: {claim_num: [claim_intepretation, ...], ..}, ...}
                for all related patents to a drug having an NDA number
        nlp (object): the nlp model loaded by spaCy.load()
    '''
    # copy mutable objects
    # label_sections_od = copy.deepcopy(label_sections_od)
    patent_no_dependency_od = copy.deepcopy(patent_no_dependency_od)

    # texts = ["This is a text", "These are lots of texts", "..."]
    # - docs = [nlp(text) for text in texts]
    # + docs = list(nlp.pipe(texts))

    # turn section text from label into spaCy Doc object using nlp.pipe for
    # improved speed
    label_sections_od_values = list(
        nlp.pipe(label_sections_od.values(), n_process=N_PROCESS))
    label_sections_od = OrderedDict(
        zip(label_sections_od.keys(), label_sections_od_values))

    # turn patent claim from multiple patents into spaCy Doc objects using
    # nlp.pipe for improved speed
    patent_no_dependency_od_values = list(
        nlp.pipe(get_values_from_od_of_od(patent_no_dependency_od),
                 n_process=N_PROCESS))
    patent_no_dependency_od = set_values_for_od_of_od(
        patent_no_dependency_od, patent_no_dependency_od_values)

    # search_doc_no_stop_words = nlp(' '.join(
    #     [str(t) for t in search_doc if not t.is_stop]))

    # for section in label_sections_od.values():
    #     section = str_to_nlp(section)

    # # turn each patent claim interpretation into a
    # for alt_intepretations in patent_no_dependency_od.values():
    #     for intepretation in alt_intepretations:
    #         alt_intepretations = str_to_nlp(section

    # print(patent_od_no_dependency)
    return_od = OrderedDict()
    for title in label_sections_od.keys():
        section_nlp = label_sections_od[title]
        if section_nlp:
            patent_claim_similarity_list = []
            for patent_num in patent_od.keys():
                for claim_num in patent_od[patent_num].keys():
                    similarity_highest = 0
                    for claim_nlp in patent_no_dependency_od[patent_num][
                            claim_num]:
                        # test each alternative claim_nlp and choose highest
                        # similarity value
                        similarity = section_nlp.similarity(claim_nlp)
                        if similarity > similarity_highest:
                            similarity_highest = similarity
                    patent_claim_similarity_list.append(
                        (patent_num, claim_num, similarity_highest))
            # sort by similarity value
            patent_claim_similarity_list.sort(key=lambda x: x[2], reverse=True)
            return_od[title] = patent_claim_similarity_list
        else:
            return_od[title] = []
    return return_od


def pretty_print_best(label_sections_od, patent_od, similarity_od):
    """
    Prints out the best claim that matches each section of the label

    Parameters:
        label_sections_od (OrderedDict): {section_title:section_text,...}
        patent_od (OrderedDict): {patent_num: {claim_num: claim_text,..},...}
        similarity_od (similarity_od): {section_title:[(patent_num, claim_num,
                                        similarity_score),...],...}
    """
    for title in label_sections_od.keys():
        print("===Title: " + title + "===")
        print(label_sections_od[title])

        if label_sections_od[title]:
            print(
                "***Top 3 Best Ranked Patent Claims (patent_num, claim_num, similarity_score):***"
            )
            top_three = similarity_od[title][:3]
            for item in top_three:
                # patent = similarity_od[title][i][0]
                # claim = similarity_od[title][i][1]
                print(item)

            print(
                "***3 Worst Ranked Patent Claims (patent_num, claim_num, similarity_score):***"
            )
            bottom_three = similarity_od[title][-3:]
            for item in bottom_three:
                print(item)


if __name__ == '__main__':

    # OrderedDict of {section_title:section_text,...}
    label_sections_od = read_label("data/label/2007-05-04.xml")

    # OrderedDict of {patent_num: {claim_num:claim_text,..},...}
    patent_od = OrderedDict()

    # OrderedDict of {patent_num: {claim_num:[claim_text,...],..},...}
    patent_od_no_dependency = OrderedDict()

    patent_files = ['8282966.xml', '8293284.xml', '8431163.xml']
    for patent_file in patent_files:
        patent_num = patent_file[:-4]
        patent_od[patent_num] = read_patent("data/patent/" + patent_file)
        patent_od_no_dependency[patent_num] = read_patent_no_dependency(
            "data/patent/" + patent_file)

    # similarity scores in OrderedDict of {section_title:[(patent_num,
    # claim_num, similarity_score),...],...} using en_core_sci_lg model
    similarity_od = label_section_to_patent_claim_similarity(
        label_sections_od, patent_od_no_dependency, en_core_sci_lg_nlp)
    print("===Most Similar Claim Selected Using en_core_sci_lg Model===")
    pretty_print_best(label_sections_od, patent_od, similarity_od)

    # # similar scores in OrderedDict selected using en_core_sci_scibert model
    # similarity_od = label_section_to_patent_claim_similarity(
    #     label_sections_od, patent_od_no_dependency, en_core_sci_scibert_nlp)
    # print("===Most Similar Claim Selected Using en_core_sci_scibert Model===")
    # pretty_print_best(label_sections_od, patent_od, similarity_od)
