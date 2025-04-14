import gettext
import locale
import os

#locale.setlocale('ru_RU', 'UTF-8')
#_podir = os.path.join(os.path.dirname(__file__), "po")
translation = gettext.translation("Wcount", "po", fallback=True)
_, ngettext = translation.gettext, translation.ngettext


DOMAIN = 'ru'
DOMAINS = {
    'ru': gettext.translation('Wcount', 'po', fallback=True),
    'en': gettext.NullTranslations()
}

def ngettext(text, textn, n):
    return DOMAINS[DOMAIN].ngettext(text, textn, n)

def _(text):
    return DOMAINS[DOMAIN].gettext(text)


while s := input(_("Input words> ")):
    cnt = len(s.split())
    print(ngettext("Entered {} word", "Entered {} words", cnt).format(cnt))
    DOMAIN = 'en'
    print(ngettext("Entered {} word", "Entered {} words", cnt).format(cnt))
    DOMAIN = 'ru'
