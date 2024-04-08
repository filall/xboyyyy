from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from bs4 import BeautifulSoup
from translate import Translator
import re

# Replace 'YOUR_TOKEN' with your actual Bot token received from BotFather
TOKEN = '6535825363:AAEZLbovwajKQ_iS1ZFcEkK46KCzYJ_oO_8'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me an AliExpress product URL and I will get the title in Arabic (for the part after the "|") and the main image for you.')

def get_product_details(url: str) -> dict:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract title
            title_tag = soup.find('meta', property='og:title')
            title = title_tag.get('content') if title_tag else "Product title not found."

            # Add parentheses around the first group of numbers (including decimals) in the title
            title = re.sub(r'(\d+(?:\.\d+)?)', r'  ثمن  👈 (\1 درهم)     \n', title, count=1)

            # Replace "MAD" with "ثمن المنتوج بالدرهم"
            title = re.sub(r'\bMAD\b', '  ', title)

            # Remove "aliexpress" from the title
            title = re.sub(r'\baliexpress\b', '', title, flags=re.IGNORECASE)

            # Replace "% OFF" with "نسبة التخفيض"
            title = re.sub(r'(\d+%)\s*OFF', r'\1 👈 نسبة التخفيض\n(ابحث جيدًا، ستجد أسعار منخفضة عبر الرابط)', title)

            # Split title at "|"
            title_parts = title.split("|")
            title_before_pipe = title_parts[0]
            title_after_pipe = "|".join(title_parts[1:]) if len(title_parts) > 1 else ""

            # Translate the part after "|" to Arabic
            translator = Translator(to_lang="ar")
            title_after_pipe_arabic = translator.translate(title_after_pipe.strip()) if title_after_pipe else ""

            # Update title tag content
            if "|" in title:
                title_tag['content'] = title_before_pipe

            # Extract image
            image_tag = soup.find('meta', property='og:image')
            image_url = image_tag.get('content') if image_tag else "Image not found."
            return {
                'title_before_pipe': title_before_pipe,
                'title_after_pipe_arabic': title_after_pipe_arabic,
                'image_url': image_url,
                'url': url
            }
        else:
            return {
                "title_before_pipe": "",
                "title_after_pipe_arabic": "Failed to retrieve the page. Please check the URL.",
                "image_url": "",
                'url': url
            }
    except Exception as e:
        return {
            'title_before_pipe': "",
            'title_after_pipe_arabic': f'An error occurred: {e}',
            'image_url': '',
            'url': url
        }

def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if 'aliexpress.com' in text and re.match(r'https?://\S+', text):
        details = get_product_details(text)
        caption = f'{details["title_before_pipe"]}\n'

        if details["title_after_pipe_arabic"]:
            caption += details["title_after_pipe_arabic"]

        caption += f'\nرابط الشراء: \n{details["url"]}'

        if details["image_url"]:
            update.message.reply_photo(photo=details["image_url"], caption=caption)
        else:
            update.message.reply_text(caption)
    else:
        update.message.reply_text('Please send a valid AliExpress product URL.')

def main() -> None:
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
