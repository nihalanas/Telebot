import asyncio
import telegram
import os
from model import calculate_cvd_score
from llama2 import gen_response
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, CallbackContext, filters
#logging.getLogger('httpx').setLevel(logging.WARNING)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#NAME, GENDER, AGE, MEDICAL_HISTORY, FINISH, ARTFIB, DONE, ADDITIONAL_DETAILS = range(8)
NAME, AGE, GENDER, ATYPICAL_ANTIPSYCHOTIC, CORTICOSTEROIDS, IMPOTENCE, MIGRAINE, RA, RENAL, SEMI, SLE, TREATEDHYP, TYPE1, TYPE2, BMI, FH_CVD, RATIO, SBP, SBPS5, SMOKE_CAT, DONE, FINISH, AF, ALC, ACTIVE, GENERATE = range(26)

gender_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="male"), KeyboardButton(text="female")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

binary_markup= ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='0'), KeyboardButton(text='1')]
              ], 
                resize_keyboard=True,
                one_time_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hey! I'm your Personal Health assistant. May I know Your Name?" , reply_markup=ReplyKeyboardRemove())
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['name'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello {user_data['name']}! Tell me your age please?")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE, reply_markup=ReplyKeyboardRemove())-> int:
    user_data = context.user_data
    user_data['age'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Select your Gender (male or female)", reply_markup=gender_markup)
    return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    user_data = context.user_data
    user_data['gender'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Is the individual affected by atrial fibrillation? (0 for No, 1 for Yes):")
    return AF

async def get_af(update: Update, context):
    user_data = context.user_data
    user_data['b_AF'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Is the individual on atypical antipsychotic medications? (0 for No, 1 for Yes):")
    return ATYPICAL_ANTIPSYCHOTIC

async def get_atypical_antipsychotic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['b_atypicalantipsy'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Is the individual on corticosteroids? (0 for No, 1 for Yes):")
    return CORTICOSTEROIDS

async def get_corticosteroids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['b_corticosteroids'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Does the individual have impotence? (0 for No, 1 for Yes):")
    return IMPOTENCE

async def get_impotence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['b_impotence'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Does the individual have a history of migraine? (0 for No, 1 for Yes):")
    return MIGRAINE

async def get_migraine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['b_migraine'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Does the individual have rheumatoid arthritis? (0 for No, 1 for Yes):")
    return RA

async def get_ra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['b_ra'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Does the individual have renal disease? (0 for No, 1 for Yes):")
    return RENAL

async def get_renal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['b_renal'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Has the individual experienced a myocardial infarction? (0 for No, 1 for Yes):")
    return SEMI

async def get_semi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['b_semi'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Does the individual have systemic lupus erythematosus? (0 for No, 1 for Yes):")
    return SLE

async def get_sle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['b_sle'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Is the individual being treated for hypertension? (0 for No, 1 for Yes):")
    return TREATEDHYP

async def get_treatedhyp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['b_treatedhyp'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Does the individual have type 1 diabetes? (0 for No, 1 for Yes):")
    return TYPE1

async def get_type1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['b_type1'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Does the individual have type 2 diabetes? (0 for No, 1 for Yes):")
    return TYPE2

async def get_type2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['b_type2'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter BMI (Body Mass Index):")
    return BMI

async def get_bmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['bmi'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Does the individual have a family history of cardiovascular disease? (0 for No, 1 for Yes):")
    return FH_CVD

async def get_fh_cvd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['fh_cvd'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter ratio of total cholesterol to HDL cholesterol:")
    return RATIO

async def get_ratio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['ratio'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter systolic blood pressure:")
    return SBP

async def get_sbp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['sbp'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter standdard deviation of at least two most recent sytolic blood pressure readings:")
    return SBPS5

async def get_sbps5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['sbps5'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter smoking category (0 for Non-smoker, 1 for Former smoker, 2 for Light smoker, 3 for Moderate smoker, 4 for Heavy smoker):")
    return SMOKE_CAT

async def get_smoke_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['smoke_cat'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Do you consume Alcohol (0 for NO, 1 for YES)")
    return ALC

async def get_alc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['alc'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Do you workout or not (0 for NO, 1 for YES)")
    return ACTIVE

async def get_active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data['active'] = update.message.text

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for providing the information. We are done!")
    return DONE
    

async def print_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    message = "Ithokke aan thaan paranhath. Sheri aano?\n"
    for key, value in user_data.items():
        message += f"{key.capitalize()}: {value}\n"
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    file_path = os.path.join("C:\\Users\\aftha\\Downloads", f"{user_data['name']}_details.txt")
    with open(file_path, "w") as file:
        file.write(message)
    
    # Send the text file to the user
    await context.bot.send_message(chat_id=update.effective_chat.id,  text="Okay ellam shekarich vechind! Pokko")
    
async def calculate_qrisk3(update: Update, context):
    user_data = context.user_data
    age= int(user_data['age'])
    bmi= float(user_data['bmi'])
    ratio= float(user_data['ratio'])
    sbp= float(user_data['sbp'])
    sbps5= float(user_data['sbps5'])
    smoke_cat=int(user_data['smoke_cat'])
    qrisk3_score = calculate_cvd_score(
        age=age,
        gender=user_data['gender'],
        b_AF=float(user_data['b_AF']),
        b_atypicalantipsy=float(user_data['b_atypicalantipsy']),
        b_corticosteroids=float(user_data['b_corticosteroids']),
        b_impotence2=float(user_data['b_impotence']),
        b_migraine=float(user_data['b_migraine']),
        b_ra=float(user_data['b_ra']),
        b_renal=float(user_data['b_renal']),
        b_semi=float(user_data['b_semi']),
        b_sle=float(user_data['b_sle']),
        b_treatedhyp=float(user_data['b_treatedhyp']),
        b_type1=float(user_data['b_type1']),
        b_type2=float(user_data['b_type2']),
        bmi=bmi,
        fh_cvd=float(user_data['fh_cvd']),
        alc=float(user_data['alc']),
        active=float(user_data['active']),

        rati=ratio,
        sbp=sbp,
        sbps5=sbps5,
        smoke_cat=smoke_cat
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your QRISK3 score is: {qrisk3_score}")
    return GENERATE

async def generate_template(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_data = context.user_data
    
    # Extract user details from user_data
    name = user_data.get('name', 'Unknown')
    gender = user_data.get('gender', 'Unknown')
    age = user_data.get('age', 'Unknown')
    height = user_data.get('height', 'Unknown')
    weight = user_data.get('weight', 'Unknown')
    bp = user_data.get('blood_pressure', 'Unknown')
    cholesterol = user_data.get('cholesterol', 'Unknown')
    bsl = user_data.get('blood_sugar_level', 'Unknown')
    smoking_category = user_data.get('smoking_category', 'Unknown')
    p_activity = user_data.get('physical_activity', 'Unknown')
    alco = user_data.get('alcohol_consumption', 'Unknown')
    qrisk_score = user_data.get('qrisk_score', 'Unknown')
    msg2="Hi"
    # Construct the message template
    message1 = f"Hi, I'm {name}, a {gender} with the following health information:\n"

    # Medical history
    message1 += f"- Atypical Antipsychotic Use: {ATYPICAL_ANTIPSYCHOTIC}\n"
    message1 += f"- Corticosteroid Use: {CORTICOSTEROIDS}\n"
    message1 += f"- Impotence: {IMPOTENCE}\n"
    message1 += f"- Migraine: {MIGRAINE}\n"
    message1 += f"- Rheumatoid Arthritis: {RA}\n"
    message1 += f"- Renal Disease: {RENAL}\n"
    message1 += f"- Sleep Apnea: {SEMI}\n"
    message1 += f"- Systemic Lupus Erythematosus: {SLE}\n"
    message1 += f"- Treated Hypertension: {TREATEDHYP}\n"
    message1 += f"- Type 1 Diabetes: {TYPE1}\n"
    message1 += f"- Type 2 Diabetes: {TYPE2}\n"

    # Physical parameters
    message1 += f"- BMI: {BMI}\n"
    message1 += f"- Family History of Cardiovascular Disease: {FH_CVD}\n"
    message1 += f"- Waist-to-Hip Ratio: {RATIO}\n"
    message1 += f"- Systolic Blood Pressure (SBP): {SBP}\n"
    message1 += f"- High SBP (>130): {SBPS5}\n"
    message1 += f"- Smoking Category: {SMOKE_CAT}\n"

    # Lifestyle habits
    message1 += f"- Alcohol Consumption: {ALC}\n"
    message1 += f"- Physical Activity Level: {ACTIVE}\n"

    message1 += "\nI would like to improve my overall health. Can you suggest 1 specific mitigation measures or lifestyle changes I can implement in one sentance?"
    print("this is the first message", message1)

    mitigation_mssg = gen_response(message1)

    print("this is the mitiagation measure from main script", mitigation_mssg)
    #return mitigation/message1 



if __name__ == '__main__':
    application = ApplicationBuilder().token('6771739826:AAE0cW8OsS67ZQMTDbZvosKh264097CfzvU').build()
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GENDER: [MessageHandler(filters.Regex(r'^(male|female)$'), get_gender)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            AF: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_af)],
            ATYPICAL_ANTIPSYCHOTIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_atypical_antipsychotic)],
            CORTICOSTEROIDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_corticosteroids)],
            IMPOTENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_impotence)],
            MIGRAINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_migraine)],
            RA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ra)],
            RENAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_renal)],
            SEMI: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_semi)],
            SLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_sle)],
            TREATEDHYP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_treatedhyp)],
            TYPE1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_type1)],
            TYPE2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_type2)],
            BMI: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_bmi)],
            FH_CVD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fh_cvd)],
            RATIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ratio)],
            SBP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_sbp)],
            SBPS5: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_sbps5)],
            SMOKE_CAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_smoke_cat)],
            ALC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_alc)],
            ACTIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_active)],
            DONE: [MessageHandler(filters.Text("Okay"), calculate_qrisk3)],
            GENERATE: [MessageHandler(filters.Text("Okay2"), generate_template)]
            #FINISH: [MessageHandler(filters.Text("Okay"), print_details)]
        },
        fallbacks=[]
    )
    
    application.add_handler(conversation_handler)
        # Add a command handler to print details later
    #print_details_handler = CommandHandler('print_details', print_details)
    #application.add_handler(print_details_handler)
    #start_handler = CommandHandler('start', start)
    #application.add_handler(start_handler)
    
    application.run_polling()
