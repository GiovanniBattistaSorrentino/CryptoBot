import re


class Utils:
    @staticmethod
    def cleanhtml(raw_html):
        CLEANR = re.compile('<.*?>')
        cleantext = re.sub(CLEANR, '', raw_html)
        return cleantext

    @staticmethod
    def replace_escapes(text: str=None) -> str:
        text = text.replace("-", "\-").replace(".", "\.").replace("[", "\[").replace("]", "\]").replace("_","\_").replace("!","\!").replace(":","\:").replace("?","\?").replace(">","\>").replace("<","\<").replace("&#39;","\'").replace("(","\(").replace(")","\)").replace("&quot;", '"').replace("+", "\+").replace("|", "\|")
        return text