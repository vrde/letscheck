# LetsCheck

## Problem

The current SARS-CoV-2 (coronavirus) outbreak proved—once again—how social media and private messaging applications are fertile ground for the spread of fake news. In particular, WhatsApp has been defined *a petri-dish of coronavirus misinformation* ([0][motherjones:petri]).

Before the coronavirus outbreak WhatsApp's effort to mitigate fake news was quite limited ([1][whatsapp:fake-news-tips], [2][cnn:fake-news-india-elections]). After the outbreak WhatsApp has been more reactive to misinformation ([3][bloomberg:fake-news-india-covid], [4][whatsapp:covid-19], [5][guardian:nhs-chatbot], [6][techcrunch:info-hub]). While those initiatives are useful, they rely on arbitrary decisions made by the WhatsApp team. Why did they choose to talk to the British National Health Service and not to the Italian Istituto Superiore di Sanità (National Institute of Health)? Why working with the Indian government and not with the German one?

Our parents, our families, our friends, our fellow citizens are constantly exposed to fake news and misinformation. Governments and medical officials are scrambling to provide the public with accurate and timely information about the novel coronavirus. But those efforts are being undermined by the spread of medical misinformation and fake cures on WhatsApp([7][cnn:coronavirus-misinformation], [8][politico:fake-news]).

Our parents, our families, our friends, our fellow citizens **deserve excellent tools** to verify the information they are exposed to.

**Closed platforms like WhatsApp don't make it easy for local organizations to act. We don't want to wait for WhatsApp to knock at our door to gift us with their help, we want to act NOW**.

If WhatsApp is not able to provide this service, then it's our duty to develop **accessible, transparent, free and open source software** to empower our communities and governments. Let's break it down:

- **Accessible**: anyone with a WhatsApp account should be able to use the service. Being able to check news should not be a privilege.
- **Transparent**: the decisional process to rate news should be auditable.
- **Free and open source software**: users have the freedom to run, copy, distribute, study, change and improve the software ([8][gnu:free-software]).

## Solution

**LetsCheck** is a free and open-source platform to empower fact-checking organizations.

**LetsCheck** provides two powerful tools:

- A WhatsApp chatbot, accessible to anyone with a WhatsApp account.
- A backoffice to process and reply to incoming messages.


A WhatsApp user can verify a message they receive by forwarding it to the chatbot. The chatbot will verify if the message is already in the database of news. If so, a reply is immediately sent to the user. If not, the message is added to the backoffice, waiting to be evaluated. Once the message has been processed, it is added to the database and a reply is sent to the user.



# Install
TBD

# Develop

Set up the database:

```
python manage.py migrate
```

You need two shells, one for the http server, another one to manage the queues.

In one shell run:

```
python manage.py runserver
```

In the other one, run:

```
python manage.py qcluster
```

# About fake-news and misinformation

## Italy

> #coronavirus: Italian regulator #AGCOM call platforms and broadcasters to make correct information and remove fake news
— https://twitter.com/InnoGenna/status/1242863421865025536


# Other links to organize

- https://drive.google.com/file/d/1KHhJCNYat68SPCuZaMRGZh747FLyx9lm/view
- https://twitter.com/EU_Commission/status/1244576714904264706
- [](https://twitter.com/InnoGenna/status/1242863421865025536)
- https://www.motherjones.com/media/2020/03/whatsapp-coronavirus-misinformation/
- https://www.buzzfeednews.com/article/nishitajha/coronavirus-india-whatsapp-rumors
- https://www.theguardian.com/world/2020/mar/20/whatsapp-in-talks-with-nhs-to-set-up-coronavirus-chatbot
- https://www.snopes.com/fact-check-ratings/


[motherjones:petri]: https://www.motherjones.com/media/2020/03/whatsapp-coronavirus-misinformation/
[whatsapp:fake-news-tips]: https://faq.whatsapp.com/26000216
[whatsapp:fake-news-video]: https://www.youtube.com/watch?v=Z2C3HD9v0uY
[cnn:fake-news-india-elections]: https://edition.cnn.com/2019/04/02/tech/whatsapp-india-tip-line-election/index.html
[techcrunch:info-hub]: https://techcrunch.com/2020/03/18/whatsapp-unveils-1m-grant-and-info-hub-to-fight-coronavirus-rumors/
[bloomberg:fake-news-india-covid]: https://www.bloombergquint.com/coronavirus-outbreak/india-launches-whatsapp-chatbot-to-curb-fake-news-on-coronavirus
[guardian:nhs-chatbot]: https://www.theguardian.com/world/2020/mar/20/whatsapp-in-talks-with-nhs-to-set-up-coronavirus-chatbot
[whatsapp:covid-19]: https://www.whatsapp.com/coronavirus
[cnn:coronavirus-misinformation]: https://edition.cnn.com/2020/03/18/tech/whatsapp-coronavirus-misinformation/index.html
[gnu:free-software]: https://www.gnu.org/philosophy/free-sw.html.en
[politico:fake-news]: https://www.politico.eu/article/the-coronavirus-covid19-fake-news-pandemic-sweeping-whatsapp-misinformation/
