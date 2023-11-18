import requests
from telegram import InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update

TOKEN = "" // Telegram bot token
API_URL = "http://apilayer.net/api/validate"
API_KEY = "" // apilayer api key

CARRIER_SUFFIXES = {
    "American Messaging Services LLC": "@page.americanmessaging.net",
    "AT&T Mobility LLC": "@txt.att.net",
    "Cellco Partnership (Verizon Wireless)": "@vtext.com",
    "Freedom Mobile Inc. (Freedom Mobile)": "@txt.freedommobile.ca",
    "MetroPCS Communications Inc.": "@mymetropcs.com",
    "New-Cell Inc. (Cellcom)": "@cellcom.quiktxt.com",
    "Rogers Communications Partnership (RCP)": "@pcs.rogers.com",
    "Sprint Corp.": "@vtext.com",
    "TELUS Corp.": "@msg.telus.com",
    "T-Mobile USA Inc.": "@tmomail.net",
    "United States Cellular Corp. (U.S. Cellular)": "@email.uscc.net",
    "USA Mobility Wireless Inc.": "@mobile.usamobility.net",
    "Alltel": "@message.alltel.com",
    "Boost Mobile": "@myboostmobile.com",
    "Cricket Wireless": "@sms.cricketwireless.net",
    "Google Fi": "@msg.fi.google.com",
    "Mint Mobile": "@mailmymobile.net",
    "Qwest": "@qwestmp.com",
    "Republic Wireless": "@text.republicwireless.com",
    "Straight Talk": "@vtext.com",
    "TracFone": "@mmst5.tracfone.com",
    "Virgin Mobile": "@vmobl.com",
    "Simple Mobile": "@smtext.com",
    "C Spire Wireless": "@cspire1.com",
    "Consumer Cellular": "@mail.consumercellular.com",
    "Pioneer Cellular": "@zsend.com",
    "nTelos": "@pcs.ntelos.com",
    "Ting": "@message.ting.com",
    "Chariton Valley Wireless": "@sms.cvalley.net",
    "Element Mobile": "@sms.elementmobile.net",
    "iWireless": "@iwirelesshometext.com",
    "Einstein PCS": "@einsteinmms.com", # For MMS
    "Airfire Mobile": "@sms.airfiremobile.com",
    "Alaska Communications": "@msg.acsalaska.com",
    "Blu": "@myblu.us", # Guess based on 2021 knowledge
    "GCI": "@mobile.gci.net",
    "Illinois Valley Cellular": "@ivctext.com",
    "Inland Cellular": "@inlandlink.com",
    "Nex-Tech Wireless": "@sms.nextechwireless.com",
    "West Central Wireless": "@sms.wcc.net",
    "Appalachian Wireless": "@sms.appwire.com",
    "Bluegrass Cellular": "@sms.bluecell.com",
    "Pine Cellular": "@sms.pinecellular.com",
    "Plateau Wireless": "@smsmail.plateautel.net",
    "DTC Wireless": "@sms.advantagecell.net",
    "Thumb Cellular": "@sms.thumbcellular.com",
    "Viaero": "@viaerosms.com",
    "Chat Mobility": "@mail.chatmobility.net",
    "Northwest Missouri Cellular": "@sms.nwmissouri.com",
    "Pioneer Wireless": "@zsend.com"  # Again, since they share the same gateway with another carrier
}


def start(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if username:  # If the user has set a username
        welcome_message = f"Welcome, {username}! Please provide phone numbers to validate."
    else:  # Some users might not have set a username, so we can fall back to first_name
        first_name = update.message.from_user.first_name
        welcome_message = f"Hello, {first_name}! Please provide phone numbers to validate."
    
    update.message.reply_text(welcome_message)

def validate_phone(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text.strip()
    phone_numbers = user_input.split('\n')
    
    valid_numbers = []
    invalid_numbers = []

    for phone_number in phone_numbers:
        params = {
            "access_key": API_KEY,
            "number": phone_number,
            "format": 1
        }
        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            data = response.json()

            carrier = data.get("carrier")
            if carrier in CARRIER_SUFFIXES:
                # Remove leading +1 or 1 from the phone number
                clean_phone_number = phone_number.lstrip('+1')
                valid_numbers.append(clean_phone_number + CARRIER_SUFFIXES[carrier])
            else:
                # Remove leading +1 or 1 from the phone number
                clean_phone_number = phone_number.lstrip('+1')
                invalid_numbers.append(clean_phone_number)

        else:
            update.message.reply_text(f"Failed to validate the phone number: {phone_number}. Please try again.")

    # Send valid numbers
    if valid_numbers:
        with open("valid_numbers.txt", "w") as valid_file:
            valid_file.write("\n".join(valid_numbers))
        with open("valid_numbers.txt", "rb") as valid_file:
            update.message.reply_document(document=InputFile(valid_file, "valid_numbers.txt"))
    else:
        update.message.reply_text("No valid numbers found.")

    # Send invalid numbers
    if invalid_numbers:
        with open("invalid_numbers.txt", "w") as invalid_file:
            invalid_file.write("\n".join(invalid_numbers))
        with open("invalid_numbers.txt", "rb") as invalid_file:
            update.message.reply_document(document=InputFile(invalid_file, "invalid_numbers.txt"))
    else:
        update.message.reply_text("No invalid numbers found.")


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, validate_phone))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
