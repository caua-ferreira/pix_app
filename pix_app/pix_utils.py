import unicodedata
import qrcode
from decimal import Decimal
from PIL import Image

def remove_acentos(s):
    if s is None:
        return ""
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')

def sanitize(s):
    if s is None:
        return ""
    return ''.join(ch for ch in s if ch >= ' ').strip()

def truncate_utf8(s, max_bytes):
    if s is None:
        return ""
    b = s.encode('utf-8')
    if len(b) <= max_bytes:
        return s
    b = b[:max_bytes]
    while b:
        try:
            return b.decode('utf-8')
        except UnicodeDecodeError:
            b = b[:-1]
    return ""

def emv(id, valor):
    tamanho = str(len(valor.encode('utf-8'))).zfill(2)
    return f"{id}{tamanho}{valor}"

def gerar_payload_pix(chave_pix, nome, cidade, valor=None, descricao=None):
    chave_pix = sanitize(chave_pix)
    nome = remove_acentos(sanitize(nome))
    cidade = remove_acentos(sanitize(cidade))
    descricao = remove_acentos(sanitize(descricao))
    payload_format = emv("00", "01")
    merchant_account_info = (
        emv("00", "BR.GOV.BCB.PIX") +
        emv("01", chave_pix)
    )
    if descricao:
        merchant_account_info += emv("02", truncate_utf8(descricao, 25))
    merchant_account_info = emv("26", merchant_account_info)
    merchant_category_code = emv("52", "0000")
    transaction_currency = emv("53", "986")
    transaction_amount = emv("54", f"{valor:.2f}") if valor else ""
    country_code = emv("58", "BR")
    merchant_name = emv("59", truncate_utf8(nome, 25))
    merchant_city = emv("60", truncate_utf8(cidade, 15))
    additional_data = emv("62", emv("05", "***"))
    payload = (
        payload_format +
        merchant_account_info +
        merchant_category_code +
        transaction_currency +
        transaction_amount +
        country_code +
        merchant_name +
        merchant_city +
        additional_data
    )
    def crc16(payload):
        polinomio = 0x1021
        resultado = 0xFFFF
        for byte in bytearray(payload.encode('utf-8')):
            resultado ^= (byte << 8)
            for _ in range(8):
                if (resultado & 0x8000):
                    resultado = ((resultado << 1) ^ polinomio) & 0xFFFF
                else:
                    resultado = (resultado << 1) & 0xFFFF
        return format(resultado, '04X')
    payload_com_crc = payload + "6304" + crc16(payload + "6304")
    return payload_com_crc

def gerar_qr_pix(payload, arquivo_saida):
    payload_final = ''.join(ch for ch in payload if ord(ch) >= 32)
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(payload_final)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#036da1", back_color="white")
    img.save(arquivo_saida)
    return arquivo_saida
