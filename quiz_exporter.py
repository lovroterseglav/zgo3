import re
from pprint import pprint

import requests
import urllib3
from bs4 import BeautifulSoup, Tag

import uuid


# def login(user, pwd):
#     authdata = {
#         'action': 'login',
#         'username': user,
#         'password': pwd
#     }
#     with session() as ses:
#         r = ses.post(baseurl + 'login/index.php', data=authdata)
#         return ses

def display(s: str):
    print(s)
    pass


def get_img(url: str):
    if not url:
        return
    cookies = {} # Moodle cookies 
    name = uuid.uuid1().__str__() + url.split("/")[-1]
    r = requests.get(url, cookies=cookies)
    with open(f"assets/{name}", "wb") as wb:
        wb.write(r.content)
    return name


def img_str(url: str):
    img_name = get_img(url)
    if img_name in [None, "unflagged"]:
        return ""

    return f"<img src=\"assets/{img_name}\" alt=\"drawing\" width=\"400\"/>"


def truefalse(tag: Tag):
    question = tag.select("div.qtext")[0]
    question_text = question.text
    img_url = None
    try:
        img_url = question.select("img")[0].attrs["src"]
    except IndexError:
        pass
    res = tag.select("div.rightanswer")[0].text.strip().removeprefix("Pravilni odgovor je '").removesuffix("'.")
    display(f"{img_str(img_url)}\n\n"
            f"{question_text}\n\n"
            f"**{res}**")


def gapselect(tag: Tag):
    img_url = None
    try:
        img_url = tag.select("img")[0].attrs["src"]
    except IndexError:
        pass
    res = tag.select("div.rightanswer")[0].text.strip().removeprefix("Pravilni odgovor odgovor je: ")
    res = res.replace("[", "**").replace("]", "**")
    display(f"{img_str(img_url)}\n\n"
            f"{res}")


def match(tag: Tag):
    question = tag.select("div.qtext")[0]
    question_text = question.text
    img_url = None
    try:
        img_url = question.select("img")[0].attrs["src"]
    except IndexError:
        pass
    res = tag.select("div.rightanswer")[0].text.strip().removeprefix("Pravilni odgovor je: ")
    res = res.split("→")
    r = [[res.pop(0).strip(), None]]
    for i in res:
        sp = i.split(",")
        r[-1][1] = sp.pop(0).strip()
        r.append([",".join(sp).strip(), None])
    r.pop(-1)

    res_str = "\n\n".join([f"**{k}** → **{v}**" for k, v in r])
    display(f"{img_str(img_url)}\n\n"
            f"{question_text}\n\n"
            f"{res_str}")


def ddwtos(tag: Tag):
    img_url = None
    try:
        img_url = tag.select("img")[0].attrs["src"]
    except IndexError:
        pass
    res = tag.select("div.rightanswer")[0].text.strip().removeprefix("Pravilni odgovor odgovor je: ")
    res_str = res.replace("[", "**").replace("]", "**")
    display(f"{img_str(img_url)}\n\n"
            f"{res_str}")


def shortanswer(tag: Tag):
    question = tag.select("div.qtext")[0]
    question_text = question.text
    img_url = None
    try:
        img_url = question.select("img")[0].attrs["src"]
    except IndexError:
        pass
    res = tag.select("div.rightanswer")[0].text.strip().removeprefix("Pravilni odgovor je: ")
    display(f"{img_str(img_url)}\n\n"
            f"{question_text}\n\n"
            f"**{res}**")


def ddimageortext(tag: Tag):
    question = tag.select("div.qtext")[0]
    question_text = question.text
    img_url = None
    try:
        img_url = tag.select("img")[0].attrs["src"]
    except IndexError:
        pass

    display(f"{img_str(img_url)}\n\n"
            f"{question_text}")


def ddmatch(tag: Tag):
    res = tag.select("div.table-responsive > table > tbody > tr")
    res = [[x.text for x in i.select("p")] for i in res]
    res_str = "\n\n".join([f"**{k}** → **{v}**" for k, v in res])

    display(res_str)


def multianswer(tag: Tag):
    res = tag.select("p")[0].text
    regex = r"Answer \d+ Vprašanje \d+"
    subst = "**[answer]**"
    result = re.sub(regex, subst, res, 0, re.MULTILINE)
    display(result)


def multichoice(tag: Tag):
    poss_answ = tag.select("p")
    res = tag.select("div.rightanswer")[0].text.strip()
    if "Pravilni odgovor je: " in res:
        res = [res.removeprefix("Pravilni odgovor je: ")]
    else:
        res = res.removeprefix("Pravilni odgovori so: ").split(", ")

    question = tag.select("div.qtext")[0]
    question_text = question.text
    img_url = None
    try:
        img_url = question.select("img")[0].attrs["src"]
        poss_answ.pop(0)
    except IndexError:
        pass

    poss_answ.pop(0)
    res_str = "- **" + "**\n\n- **".join(res) + "**"
    display(f"{img_str(img_url)}\n\n"
            f"{question_text}\n\n"
            f"{res_str}")


r = {'shortanswer', 'ddwtos', 'multichoice', 'match', 'gapselect', 'truefalse', 'multianswer', 'ddmatch', 'ddimageortext'}
rn = set()
for quiz_file in ["rim_kraljevina.html", "rim_republika.html", "rimska_vojska.html",
                  "propad_rimske_republike_in_ustanovitev_cesarstva.html", "rimsko_cesarstvo.html"]:
    print(f"\n\n---\n\n")
    print(f"# {quiz_file}\n")
    with open(quiz_file) as f:
        soup = BeautifulSoup(f.read(), "html5lib")

    page = soup.select('div#page-content')[0]
    questions = page.select("form > div > div")
    questions.pop(-1)

    for q in questions:
        qtype = q.attrs["class"][1]
        num = int(q.select("span.qno")[0].text)
        points = float(q.select("div.grade")[0].text.removeprefix("Ocenjen od ").replace(",", "."))
        display(f"## {num} ({points})")
        rn.add(qtype)
        match qtype:
            case "multichoice":
                multichoice(q)
            case "shortanswer":
                shortanswer(q)
            case "ddwtos":
                ddwtos(q)
            case "match":
                match(q)
            case "gapselect":
                gapselect(q)
            case "truefalse":
                truefalse(q)
            case "ddimageortext":
                ddimageortext(q)
            case "ddmatch":
                ddmatch(q)
            case "multianswer":
                multianswer(q)
print(rn - r)
