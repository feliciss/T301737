# Example bot for T301737 (https://phabricator.wikimedia.org/T301737) task
# (C) Feliciss, task completed on 11-April-2022

from pywikibot import ItemPage, Site, PropertyPage
from pywikibot.site import DataSite
from pywikibot.exceptions import InvalidTitleError


# get_property_values_from_an_item
def get_property_values_from_an_item(data_site, item, prop, label, language) -> list:
    # get item page
    item_page = ItemPage(data_site, item)
    # construct list of multiple property values
    values = []
    for item in item_page.claims[prop]:
        target = item.getTarget()
        title = target.title()
        itm_page = ItemPage(data_site, title)
        value = itm_page.get()[label][language]
        values.append(value)
    return values


# get_qualifiers_from_a_claim
def get_qualifiers_from_a_claim(data_site, claim, label, language) -> tuple:
    qualifiers = claim.qualifiers
    names = []
    targets = []
    for qualifier in qualifiers:
        for claim in qualifiers[qualifier]:
            claim_id = claim.getID()
            property_page = PropertyPage(data_site, claim_id)
            name = property_page.get()[label][language]
            target = claim.getTarget()
            names.append(name)
            targets.append(target)
    return names, targets


class T301737Bot:

    def __init__(self, source):
        self.source = source

    # get_data_site: get and connect data site
    def get_data_site(self) -> DataSite:
        # connect site
        site = Site(self.source, self.source)
        repo = site.data_repository()
        return repo

    # print_property_value_from_a_page: now only supports printing author names on Wikidata items page
    def print_property_value_from_a_page(self, items, properties, label,
                                         language) -> None:
        # get data site
        data_site = self.get_data_site()
        # code refers to https://www.wikidata.org/wiki/Wikidata:Creating_a_bot#Example_11:_Get_values_of_sub-properties
        # and https://github.com/mpeel/wikicode/blob/master/example.py
        for item in items:
            item_page = ItemPage(data_site, item)
            for prop in properties:
                if prop in item_page.claims:
                    for claim in item_page.claims[prop]:
                        target = claim.getTarget()
                        names, targets = get_qualifiers_from_a_claim(data_site, claim, label, language)
                        try:
                            given_name_property = 'P735'
                            family_name_property = 'P734'
                            title = target.title()
                            given_name = get_property_values_from_an_item(data_site, title, given_name_property, label,
                                                                          language)
                            family_name = get_property_values_from_an_item(data_site, title, family_name_property,
                                                                           label,
                                                                           language)
                            print('Given Name:', *given_name, 'Family Name:', *family_name, dict(zip(names, targets))
                            if names else '')
                        except InvalidTitleError:
                            print(target, dict(zip(names, targets)) if names else '')


def main(*args: str) -> None:

    # set source
    source = 'wikidata'

    # init T301737 bot
    bot = T301737Bot(source)

    # print property value from a page
    bot.print_property_value_from_a_page(['Q56603073'], ['P2093', 'P50'], 'labels', 'en')


if __name__ == '__main__':
    main()
