import os
import requests
import logging
from datetime import datetime
from telegram import Bot, Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue

# Configurazione
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Database squadre (verrà aggiornato)
TEAM_STATS = {
    "Juventus": {"under_05_ht": 82, "avg_goals_ht": 0.18},
    "Inter": {"under_05_ht": 75, "avg_goals_ht": 0.32},
    "Milan": {"under_05_ht": 78, "avg_goals_ht": 0.28},
    "Verona": {"under_05_ht": 92, "avg_goals_ht": 0.12},
    "Lecce": {"under_05_ht": 88, "avg_goals_ht": 0.15}
}

def generate_recommendations():
    """Genera raccomandazioni (demo)"""
    today = datetime.now().strftime('%d/%m')
    return [
        {
            "match": "Verona vs Lecce",
            "time": "20:45",
            "prob_under": 90,
            "reasons": [
                f"• Verona: 92% Under 0.5 HT (casa)",
                f"• Lecce: 88% Under 0.5 HT (trasferta)",
                f"• Media gol/1T: 0.15"
            ]
        },
        {
            "match": "Cagliari vs Juventus",
            "time": "21:00",
            "prob_under": 83,
            "reasons": [
                f"• Cagliari: 85% Under 0.5 HT",
                f"• Juventus: 82% Under 0.5 HT",
                f"• Media gol/1T: 0.20"
            ]
        }
    ]

def send_daily_matches(context: CallbackContext):
    """Invio giornaliero"""
    try:
        chat_id = context.job.context
        recs = generate_recommendations()
        
        message = "🔮 *PRONOSTICI UNDER 0.5 PRIMO TEMPO*:\n\n"
        for i, rec in enumerate(recs, 1):
            message += (
                f"⚽️ *Match {i}:* {rec['match']}\n"
                f"⏰ {rec['time']} | 📊 Prob: {rec['prob_under']}%\n"
                f"📌 *Motivi:*\n" + "\n".join(rec['reasons']) + "\n\n"
            )
        
        context.bot.send_message(
            chat_id,
            message + "⚠️ *Nota:* Bot in versione demo, dati reali verranno aggiunti",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Errore: {str(e)}")

def start(update: Update, context: CallbackContext):
    """Attiva notifiche"""
    chat_id = update.message.chat_id
    context.job_queue.run_daily(
        send_daily_matches,
        time=datetime.strptime("08:00", "%H:%M").time(),
        context=chat_id
    )
    update.message.reply_text(
        "✅ Bot attivato! Riceverai pronostici giornalieri alle 08:00 UTC\n\n"
        "🔧 *Stato:* Versione demo 1.0\n"
        "⚙️ *Prossimo aggiornamento:* Scraping dati in tempo reale",
        parse_mode=ParseMode.MARKDOWN
    )

def main():
    """Avvia il bot"""
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()