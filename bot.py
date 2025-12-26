import os
import logging
import tempfile
import subprocess
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token bot (ganti dengan token Anda)
TOKEN = "8526239051:AAGw0qU5L6WBdJaenoKuPFD5gMdsOOSAmGA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start"""
    await update.message.reply_text(
        "Halo! Kirimkan gambar QR code dengan ekstensi .jpg "
        "dan saya akan memprosesnya menggunakan tikqr.py"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /help"""
    await update.message.reply_text(
        "Bot untuk memproses file QR code:\n"
        "1. Kirim file gambar dengan ekstensi .jpg\n"
        "2. Bot akan memproses dengan tikqr.py\n"
        "3. Hasil akan dikirim kembali sebagai pesan"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk file document"""
    try:
        document = update.message.document
        
        # Cek ekstensi file
        if not document.file_name.lower().endswith('.jpg'):
            await update.message.reply_text("Silakan kirim file dengan ekstensi .jpg")
            return
        
        # Kirim status sedang memproses
        processing_msg = await update.message.reply_text("⏳ Memproses file...")
        
        # Download file
        file = await document.get_file()
        
        # Buat direktori temporary
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, document.file_name)
            
            # Download file ke temporary directory
            await file.download_to_drive(file_path)
            
            # Jalankan tikqr.py dengan subprocess
            result = subprocess.run(
                ['python', 'tikqr.py', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Hapus pesan proses
            await processing_msg.delete()
            
            if result.returncode == 0 and result.stdout:
                # Kirim hasil yang berhasil
                if len(result.stdout) > 4000:
                    # Jika hasil terlalu panjang, kirim sebagai file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                        f.write(result.stdout)
                        f.flush()
                    
                    with open(f.name, 'rb') as f:
                        await update.message.reply_document(
                            document=f,
                            filename='hasil_tikqr.txt',
                            caption="Hasil pemrosesan QR Code"
                        )
                    
                    os.unlink(f.name)
                else:
                    await update.message.reply_text(f"✅ Hasil pemrosesan:\n\n```json\n{result.stdout}\n```", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Gagal memproses file. Pastikan file berisi QR code yang valid.")
                logger.error(f"Error: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        await update.message.reply_text("⏰ Timeout: Proses terlalu lama")
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        await update.message.reply_text(f"❌ Terjadi error: {str(e)}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk photo (jika user mengirim sebagai photo)"""
    await update.message.reply_text(
        "Silakan kirim file sebagai Document (pilih file) dengan ekstensi .jpg, "
        "bukan sebagai photo untuk kualitas terbaik."
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk error"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("Maaf, terjadi error. Silakan coba lagi.")

def main():
    """Main function untuk menjalankan bot"""
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Jalankan bot
    print("Bot sedang berjalan...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
