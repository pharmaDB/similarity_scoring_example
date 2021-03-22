import scispacy
import spacy
from load_file import read_label, read_patent, read_patent_no_dependency
from collections import OrderedDict

# load scispaCy models
en_core_sci_lg_nlp = spacy.load(
    "en_core_sci_lg-0.4.0/en_core_sci_lg/en_core_sci_lg-0.4.0")
en_core_sci_scibert_nlp = spacy.load(
    "en_core_sci_scibert-0.4.0/en_core_sci_scibert/en_core_sci_scibert-0.4.0/")

# cache for nlp object each consisting of [string, nlp_object]
string_nlp_list1 = [""] * 2
string_nlp_list2 = [""] * 2


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


def label_section_to_patent_claim_similarity(labels_section_od,
                                             patent_od_no_dependency, method):
    '''
    Returns OrderedDict of {section_title:[(patent_num, claim_num,
    similarity_score),...],...} wherein each (patent_num, claim_num,
    similarity_score) for a label section, as defined by section_title, is
    sorted from the most similar to most dissimilar claim.

    Parameters:
        labels_section_od (OrderedDict): {section_title:section_text,...}
        patent_od_no_dependency (OrderedDict): {patent_num: {claim_num:
                                                [claim_text, ...], ..}, ...}
        method (object): the model loaded by spaCy.load()
    '''
    return_od = OrderedDict()
    for title in label_sections_od.keys():
        section_text = label_sections_od[title]
        if section_text:
            patent_claim_similarity_list = []
            for patent_num in patent_od.keys():
                for claim_num in patent_od[patent_num].keys():
                    similarity_highest = 0
                    for claim_text in patent_od[patent_num][claim_num]:
                        # test each alternative claim_text and choose
                        # highest similarity value
                        similarity = get_similarity(
                            section_text, claim_text, method)
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
                "***Top 3 Best Ranked Patent Claims (patent_num, claim_num, similarity_score):***")
            for i in range(1, 4):
                patent=similarity_od[title][i][0]
                claim=similarity_od[title][i][1]
                print(similarity_od[title][i])


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
            "data/" + patent_file)

    # similarity scores in OrderedDict of {section_title:[(patent_num,
    # claim_num, similarity_score),...],...} using en_core_sci_lg model
    similarity_od = label_section_to_patent_claim_similarity(
        label_sections_od, patent_od_no_dependency, en_core_sci_lg_nlp)
    print("===Most Similar Claim Selected Using en_core_sci_lg Model===")
    pretty_print_best(label_sections_od, patent_od, similarity_od)

    # similar scores in OrderedDict selected using en_core_sci_scibert model
    similarity_od = label_section_to_patent_claim_similarity(
        label_sections_od, patent_od_no_dependency, en_core_sci_scibert_nlp)
    print("===Most Similar Claim Selected Using en_core_sci_scibert Model===")
    pretty_print_best(label_sections_od, patent_od, similarity_od)
