import requests
from bs4 import BeautifulSoup
import telegram

# Replace with your bot token
bot_token = "7076261734:AAH4-Xs0v2IaF87lD73W3PyuMXTaCgX_VjU"

# Function to get product information from AliExpress
def get_product_info(url):
    # Handle shortened AliExpress URLs (https://s.click.aliexpress.com)
    if url.startswith("https://s.click.aliexpress.com"):
        # Use the AliExpress API to retrieve the actual product URL
        api_url = f"https://api.click.aliexpress.com/rest/convertUrl?shortUrl={url}"
        response = requests.get(api_url)
        product_url = response.json()["data"]["longUrl"]
    else:
        # Remove any trailing text after the product ID
        product_id = re.search(r"https://\w+\.aliexpress\.com/item/(.+?)\.html", url).group(1)
        product_url = f"https://www.aliexpress.com/item/{product_id}.html"

    response = requests.get(product_url)
    soup = BeautifulSoup(response.content, "lxml")

    # Get product title
    title = soup.find("h1", class_="product-title-text").text.strip()

    # Get product image URL
    image_url = soup.find("img", class_="magnifier-image")["src"]

    return title, image_url

# Initialize Telegram bot
bot = telegram.Bot(token=bot_token)

# Function to handle incoming messages
def handle_message(update, context):
    chat_id = update.message.chat_id
    text = update.message.text

    # Check if message starts with "/product"
    if text.startswith("/product"):
        # Extract product URL from message
        product_url = text.split()[1]

        # Get product information
        title, image_url = get_product_info(product_url)

        # Send product information to user
        bot.send_message(chat_id, f"**Title:** {title}\n**Image URL:** {image_url}")

# Start the bot
bot.updater.dispatcher.add_handler(telegram.MessageHandler(filters=telegram.Filters.text, callback=handle_message))
bot.updater.start_polling()
bot.updater.idle()