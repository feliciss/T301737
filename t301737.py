# Example bot for T301737 (https://phabricator.wikimedia.org/T301737) task
# (C) Feliciss, task completed on 11-April-2022

from pywikibot import ItemPage, Site, Claim
from pywikibot.site import DataSite
from pywikibot.exceptions import InvalidTitleError

# use ads environment
import ads
import re


def get_author_names_from_ads(bibcodes) -> list:
    articles = [list(ads.SearchQuery(bibcode=bibcode))[0] for bibcode in
                bibcodes]
    first_paper = articles[0]
    return first_paper.author


def put_author_name_in_regex(author) -> str:
    # divide author first and last name
    names = divide_author_names(author)
    # divide abbrev by whitespace
    abbrevs = names[1].split(' ')
    # reconstruct with regex *
    abbrevs_for_regex = [abbrev.replace('.', '.*') for abbrev in abbrevs]
    # merge and rejoin strings
    first_name_regex = ' '.join(abbrevs_for_regex)
    # join first and last names together
    full_name_regex = first_name_regex + ' ' + names[0]
    # return full name
    return full_name_regex


def divide_author_names(author) -> list:
    # divide author first and last name
    names = author.split(', ')
    return names


class T301737Bot:

    def __init__(self, source):
        self.source = source

    # get_data_site: get and connect data site
    def get_data_site(self) -> DataSite:
        # connect site
        site = Site(self.source, self.source)
        repo = site.data_repository()
        return repo

    # get_items_value_from_a_page: modified from Task 2 (print_property_value_from_a_page)
    def get_items_value_from_a_page(self, items, properties, label,
        language, command, names_in_source_of_truth=[], wikidata_name_list=[]) -> {}:
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
                        try:
                            title = target.title()
                            title_page = ItemPage(data_site, title)
                            wikidata_full_name = title_page.get()[label][
                                language]
                            match command:
                                case 'get_wikidata_items':
                                    wikidata_name_list.append(wikidata_full_name)
                                case 'print_sources_and_add_qualifiers':
                                    self.print_sources_and_add_qualifiers(
                                        names_in_source_of_truth,
                                        wikidata_full_name, claim)
                                case _:
                                    return 'Please enter a command.'
                        except InvalidTitleError:
                            match command:
                                case 'get_wikidata_items':
                                    wikidata_name_list.append(target)
                                case 'print_sources_and_add_qualifiers':
                                    self.print_sources_and_add_qualifiers(
                                        names_in_source_of_truth,
                                        target, claim)
                                case _:
                                    return 'Please enter a command.'

    # print_sources_and_add_qualifiers: Step 4 and 5: print sources together
    # and save the names from ADS to Wikidata qualifier
    def print_sources_and_add_qualifiers(self, names_in_source_of_truth, target,
        claim) -> None:
        for name_in_sot in names_in_source_of_truth:
            # put ads author names to regex form
            full_name_regex = put_author_name_in_regex(name_in_sot)
            # match full_name_regex with wikidata name
            matched = re.search(rf'{full_name_regex}', target)
            if matched:
                    # print values
                    print('{:<20s}{:<20s}'.format(matched.string, name_in_sot))
                    # save to Wikidata item
                    names = divide_author_names(name_in_sot)
                    given_name_qualifiers = self.set_qualifier_targets(names[1],
                                                                       'P9687')
                    last_name_qualifiers = self.set_qualifier_targets(names[0],
                                                                      'P9688')
                    claim.addQualifier(last_name_qualifiers,
                                       summary=f'Adding last name qualifier to {target}')
                    claim.addQualifier(given_name_qualifiers,
                                       summary=f'Adding given name qualifier to {target}')

    # set_qualifier_targets
    def set_qualifier_targets(self, target, prop) -> Claim:
        # get data site
        data_site = self.get_data_site()
        # set qualifier
        qualifier = Claim(data_site, prop)
        qualifier.setTarget(target)
        return qualifier


def main(*args: str) -> None:
    # set source to update
    source = 'wikidata'

    # init T301737 bot
    bot = T301737Bot(source)

    # set parameters
    items = ['Q56603073']
    properties = ['P2093', 'P50']
    label = 'labels'
    language = 'en'

    # set print wikidata command
    get_wikidata_items_command = 'get_wikidata_items'

    # set a name list
    wikidata_name_list = []

    # Step 2: print author names from Wikidata
    bot.get_items_value_from_a_page(items, properties,
                                                          label, language,
                                                          get_wikidata_items_command, wikidata_name_list=wikidata_name_list)
    print('Author names from Wikidata: \n', wikidata_name_list)

    # set ads as source of truth
    bibcodes = ['2011PASP..123..568C']
    names_in_source_of_truth = get_author_names_from_ads(bibcodes)

    # Step 3: print author names from ADS
    print('Author names from NASA ADS: \n', names_in_source_of_truth)

    # print header line
    print('Author names from both sources: \n{:<20s}{:<20s}'.format('Wikidata', 'NASA ADS'))

    # set print sources command
    print_sources_and_add_qualifiers_command = 'print_sources_and_add_qualifiers'

    # Step 4 and 5: print both sources and save names to qualifier value
    bot.get_items_value_from_a_page(
        items,
        properties,
        label, language,
        print_sources_and_add_qualifiers_command,
        names_in_source_of_truth=names_in_source_of_truth)


if __name__ == '__main__':
    main()
