from faker import Faker
import json
from unidecode import unidecode
import pyarabic.trans as trans

# List of locales you are interested in
# locales = [
#     "ar_AA",
#     "ar_JO",
#     "ar_SA",
#     "bg_BG",
#     "bs_BA",
#     "cs_CZ",
#     "de_AT",
#     "de_CH",
#     "de_DE",
#     "dk_DK",
#     "el_GR",
#     "en_AU",
#     "en_CA",
#     "en_GB",
#     "en_IE",
#     "en_IN",
#     "en_NZ",
#     "en_TH",
#     "en_US",
#     "es_ES",
#     "es_MX",
#     "et_EE",
#     "fa_IR",
#     "fi_FI",
#     "fr_FR",
#     "fr_CA",
#     "he_IL",
#     "hi_IN",
#     "hr_HR",
#     "hu_HU",
#     "hy_AM",
#     "id_ID",
#     "it_IT",
#     "ja_JP",
#     "ka_GE",
#     "ko_KR",
#     "lt_LT",
#     "lv_LV",
#     "ne_NP",
#     "nl_BE",
#     "nl_NL",
#     "no_NO",
#     "pl_PL",
#     "pt_BR",
#     "pt_PT",
#     "ro_RO",
#     "ru_RU",
#     "sl_SI",
#     "sv_SE",
#     "tr_TR",
#     "uk_UA",
#     "zh_CN",
#     "zh_TW",
# ]  # Italian, American, Japanese, German, Spanish names

locales = ["ar_EG", "ar_PS", "az_AZ", "zu_ZA"]

data = {}
print("Begin...")
for locale in locales:
    count = 10000
    tries_max = 100
    tries = 0
    print(locale)
    fake = Faker(locale)
    unique_first_names = set()  # Use a set to store unique names
    unique_last_names = set()  # Use a set to store unique names
    while len(unique_first_names) < count:
        first_name = (
            fake.first_name_male()
            if hasattr(fake, "first_name_male")
            else fake.first_name()
        )
        f_n_l = " ".join(unidecode(first_name).split())
        # Add to the set if not already present (sets automatically ensure uniqueness)
        if f_n_l in unique_first_names:
            tries += 1
            if tries > tries_max:
                break
        else:
            unique_first_names.add(f_n_l)
            if tries > 0:
                tries = 0

    tries = 0
    while len(unique_last_names) < count:
        last_name = (
            fake.last_name_male()
            if hasattr(fake, "last_name_male")
            else fake.last_name()
        )
        # Add to the set if not already present (sets automatically ensure uniqueness)
        l_n_l = " ".join(unidecode(last_name).split())
        if l_n_l in unique_last_names:
            tries += 1
            if tries > tries_max:
                break
        else:
            unique_last_names.add(l_n_l)
            if tries > 0:
                tries = 0

    # Convert each tuple in the set to a dictionary and add to data
    data[locale] = {
        "first_names": [],
        "last_names": [],
    }
    data[locale]["first_names"] = [name for name in unique_first_names]
    data[locale]["last_names"] = [name for name in unique_last_names]

# Writing the names to a JSON file
with open("unique_male_names_by_country.json", "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

print("JSON file created with unique male names grouped by country.")
