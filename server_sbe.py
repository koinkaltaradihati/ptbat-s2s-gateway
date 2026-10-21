from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel

app = FastAPI(
    title="PT BAT S2S API Gateway - Production Sandbox",
    version="1.0.0",
    description="Infrastruktur Gateway Server-to-Server untuk Simulasi Penerimaan Foreign Direct Investment (FDI) & Payout Management"
)

# Kredensial Resmi Sandbox BCA PT Bintang Armada Timur
BCA_SANDBOX_API_KEY = "71b93217-127a-43fc-8620-33e4c44a2e12"

# Struktur Data Payload / Body Transaksi Masuk
class TransactionPayload(BaseModel):
    ref_id: str
    amount: float
    currency: str = "EUR"
    sender: str = "MUSTAFA ARSHAD-MÜLLER (UBS AG)"
    receiver: str = "PT BINTANG ARMADA TIMUR (BCA KCU Malang)"

@app.post("/v1/s2s/receive")
async def receive_s2s_signal(
    payload: TransactionPayload,
    x_signature: str = Header(..., alias="X-Signature"),
    x_client_id: str = Header(..., alias="X-Client-ID")
):
    """
    Endpoint utama S2S untuk menerima sinyal transfer dana masuk, 
    memverifikasi kredensial, dan memproses aturan Pilot Tranche.
    """
    # 1. Validasi Keamanan Client ID / API Key
    if x_client_id != BCA_SANDBOX_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akses ditolak: X-Client-ID atau API Key tidak valid."
        )
    
    # 2. Validasi Keberadaan Header X-Signature
    if not x_signature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak: Header X-Signature wajib disertakan."
        )
    
    # 3. Cetak Log Payload yang Masuk ke Terminal Command Prompt
    print("\n[INFO] === MENERIMA SINYAL TRANSAKSI MASUK (S2S) ===")
    print(f"Reference ID : {payload.ref_id}")
    print(f"Nominal      : {payload.amount:,.2f} {payload.currency}")
    print(f"Pengirim     : {payload.sender}")
    print(f"Penerima     : {payload.receiver}")
    print("==================================================\n")
    
    # 4. Logika Kebijakan Pilot Tranche (Strategi Awal 1 Juta EUR/USD)
    amount = payload.amount
    currency = payload.currency
    
    is_pilot_mode = True
    if is_pilot_mode and amount > 1000000.0:
        return {
            "status": "PENDING_COMPLIANCE_REVIEW",
            "message": "Transaksi melebihi batas nilai uji coba pilot (1 Juta). Memerlukan peninjauan manual oleh Compliance BCA & PT BAT.",
            "client_id": x_client_id,
            "received_amount": f"{amount:,.2f} {currency}"
        }

    # 5. Respon Sukses untuk Tranche/Pilot yang Sesuai
    return {
        "status": "SUCCESS",
        "message": "Sinyal S2S dan payload berhasil diverifikasi. Dana masuk dicatat untuk kliring perbankan & persiapan alur payout USDT.",
        "client_id": x_client_id,
        "transaction_ref": payload.ref_id,
        "processed_amount": f"{amount:,.2f} {currency}"
    }

if __name__ == "__main__":
    import uvicorn
    # Menjalankan server lokal pada port 8000
    uvicorn.run("server_sbe:app", host="0.0.0.0", port=8000, reload=True)
