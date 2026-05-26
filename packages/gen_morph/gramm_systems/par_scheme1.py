from collections.abc import Iterable
from library.tables.table_scheme import TableScheme

class ParadigmScheme:
    
    def __init__(self, properties: dict[str, list[str]],
                 categories: list[str],
                 pos_implic: dict[str, list[str]],
                 neg_implic: dict[str, list[str]],
                 implied: set[str]):
        self.properties = properties
        self.categories = categories
        self.pos_implic = pos_implic
        self.neg_implic = neg_implic
        self.implied = implied

    def is_implied(self, category: str) -> bool:
        return category in self.implied

    def pos_implies(self, gramm_form: Iterable[str], category: str) -> bool:
        for prop in self.pos_implic:
            if prop in gramm_form:
                if category in self.pos_implic[prop]:
                    return True
        return False

    def neg_implies(self, gramm_form: Iterable[str], category: str) -> bool:
        for prop in self.neg_implic:
            if prop in gramm_form:
                if category in self.neg_implic[prop]:
                    return True
        return False

    def get_gramm_forms(self) -> list[dict[str, str]]:
        i = 0
        gramm_form = dict[str, str]()
        gramm_forms = list[dict[str, str]]()
        self.step(i, gramm_form, gramm_forms)
        return gramm_forms

    def step(self, i: int, gramm_form: dict[str, str], gramm_forms: list[dict[str, str]]):
        if i == len(self.categories):
            gramm_forms.append(gramm_form)
        else:
            category = self.categories[i]
            properties = gramm_form.values()
            if (not self.is_implied(category) or self.pos_implies(properties, category)) and not self.neg_implies(properties, category):
                for prop in self.properties[category]:
                    new_gramm_form = gramm_form.copy()
                    new_gramm_form[category] = prop
                    self.step(i+1, new_gramm_form, gramm_forms)
            else:
                self.step(i+1, gramm_form, gramm_forms)

    def headers_step(self, i: int, gramm_form: list[str], gramm_forms: list[list[str]], categories: list[str], table=False):
        if i == len(categories):
            gramm_forms.append(gramm_form)
        else:
            category = categories[i]
            if (not self.is_implied(category) or self.pos_implies(gramm_form, category) or table) \
            and not self.neg_implies(gramm_form, category):
                for prop in self.properties[category]:
                    new_gramm_form = gramm_form.copy()
                    new_gramm_form.append(prop)
                    self.headers_step(i+1, new_gramm_form, gramm_forms, categories, table)
            else:
                new_gramm_form = gramm_form.copy()
                new_gramm_form.append('_')
                self.headers_step(i+1, new_gramm_form, gramm_forms, categories, table)

    def get_headers(self, categories: list[str]) -> list[list[str]]:
        i = 0
        gramm_form = list[str]()
        gramm_forms = list[list[str]]()
        self.headers_step(i, gramm_form, gramm_forms, categories, True)
        return gramm_forms

    def get_table_scheme(self, row_cats: list[str], col_cats: list[str]) -> TableScheme:
        row_headers = self.get_headers(row_cats)
        col_headers = self.get_headers(col_cats)
        return TableScheme(row_cats, col_cats, row_headers, col_headers)
    
