import lxml
from bs4 import BeautifulSoup as bs
from collections import OrderedDict
from no_dependent_claim import dependent_to_independent_claim
import re


def read_label(label_file):
    """
    Returns an OrderedDict with {section_title:section_text,...} for an label
    XML file.

    Parameters:
        label_file (string): filename of the label XML file.
    """

    content = []
    with open(label_file, "r") as file:
        # readlines returns list of lines
        content = file.readlines()
        # join list into string
        content = "".join(content)
        # turn string into BeautifulSoup object
        bs_content = bs(content, "lxml")

    # find all elements between title tags
    all_titles = bs_content.find_all("title")

    # OrderedDict of {title: content} for all sections of label
    label_sections_od = OrderedDict()

    for title in all_titles:
        # if title has subtitles, just add title to the OrderedDict
        if len(title.parent.find_all('title')) > 1:
            label_sections_od[title.text] = ""
        else:
            label_sections_od[title.text] = title.parent.find("text").text
    return label_sections_od


def read_patent(patent_file):
    """
    Returns an OrderedDict for a patent XML with {claim_num:claim_text}

    Parameters:
        label_file (string): filename of the label XML file.
    """

    with open(patent_file, "r") as file:
        # readlines returns list of lines
        content = file.readlines()
        # join list into string
        content = "".join(content)
        # turn string into BeautifulSoup object
        bs_content = bs(content, "lxml")

    all_claims_list = bs_content.find_all(
        "claim", {"id": re.compile(r'CLM-.*', re.IGNORECASE)})

    claims_od = OrderedDict()

    for claim_xml in all_claims_list:
        claim_num = int(claim_xml['num'])
        claims_od[claim_num] = claim_xml.text

    # dependent claims in claims_od are put into independent claim form
    return claims_od


def read_patent_no_dependency(patent_file):
    """
    Returns an OrderedDict for a patent XML with {claim_num:[claim_text, ...],
    ..}, ...}.  Each claim_text is the patent claim written in independent form
    without any dependency to parent claims.

    Parameters:
        label_file (string): filename of the label XML file.
    """
    # dependent claims in claims_od are put into independent claim form
    return dependent_to_independent_claim(read_patent(patent_file))


if __name__ == '__main__':

    label_sections_od = read_label("data/2007-05-04.xml")

    # # printout of label_sections_od
    # for title in label_sections_od.keys():
    #     print("===Title: " + title + "===")
    #     print(label_sections_od[title])

    # OrderedDict of {patent_num: {claim_num:[claim_text,...],..},...}
    patent_od = OrderedDict()

    patent_files = ['8282966.xml', '8293284.xml', '8431163.xml']
    for patent_file in patent_files:
        patent_num = patent_file[:-4]
        patent_od[patent_num] = read_patent_no_dependency("data/" +
                                                          patent_file)

        # printout of content of patent_od
        print("===Patent: US" + patent_num + "===")
        for claim_num in patent_od[patent_num].keys():
            print("Claim " + str(claim_num) + ":")
            print(patent_od[patent_num][claim_num])
