# T301737
What's in a name? Task 3

## Output

Code output [reference](./out/t301737.adoc).

## Install 
This code uses ads client. To run this code, install ads python library:
```bash
pip3 install ads
```

## Setting 

### Get Token
Visit https://ui.adsabs.harvard.edu/user/settings/token to get a token.

### Set Token
This code uses a token from ADS. To run, set a token either by environment variable or a file:

#### Environment variable

```bash
export ADS_DEV_KEY=<token>
```

#### File

```bash
echo <token> > ~/.ads/dev_key
```

### Pywikibot

You need to log in as a Wikidata user for this code to make any changes to Wikidata.

```bash
python3 pwb.py login
```