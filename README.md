
![avatar](https://images.weserv.nl/?url=github.com/david-lev/hebrewbooksbot/assets/42866208/ab932b89-6dbd-473e-8f93-849db7f8b244?v=4&h=150&w=150&fit=cover&mask=circle&maxage=7d)


# HebrewBooksBot

**A bot that allows you to search and browse books from [hebrewbooks.org](https://hebrewbooks.org).**

- Telegram: [@HeBooksBot](https://t.me/HeBooksBot)
- WhatsApp: [+1 (929) 647-6710](https://wa.me/19296476710) (Countries limited)

---
### Features
- Search for books by title and author
- Browse books by category, date or letter
- Browse masechtos
- Instant Reading Mode as Image or PDF
- Download and share books
- Jump to page
- Support for Hebrew and English
---

TODO:
- [x] Adding support for WhatsApp!
- [ ] Add support for text in reading mode
- [ ] Add support for search by OCR
- [ ] Allows users to change their language
- [ ] Allows users to save their favorite books and bookmarks

---
### Running the bot
1. Clone the repository
2. Copy `.env.example` to `.env` and fill in the values

With Docker:
```bash
docker compose up
```
Directly:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 tg/app.py  # for Telegram
python3 wa/app.py  # for WhatsApp
```

