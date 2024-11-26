import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

# Fungsi untuk mengklasifikasikan jarak dari pantai
def klasifikasi_jarak(jarak):
    if 0 <= jarak <= 25:
        return "Dekat"
    elif 26 <= jarak <= 100:
        return "Sedang"
    elif jarak > 100:
        return "Jauh"
    else:
        return "Tidak Valid"

# Fungsi untuk mengklasifikasikan kedalaman
def klasifikasi_kedalaman(kedalaman):
    if kedalaman <= 15:
        return "Dalam"
    elif kedalaman > 15:
        return "Sangat Dalam"
    else:
        return "Tidak Valid"

# Fungsi untuk mengklasifikasikan skala gempa
def klasifikasi_skala(skala):
    if skala < 5.0:
        return "Kecil"
    elif 5.1 <= skala <= 7.0:
        return "Sedang"
    elif skala > 7.0:
        return "Tinggi"
    else:
        return "Tidak Valid"

# Fungsi untuk menentukan efek gempa
def tentukan_efek(jarak, kedalaman, skala_numerik):
    if skala_numerik > 7.0:
        if jarak == "Dekat" or kedalaman == "Dalam":
            return "Tsunami"
        elif kedalaman == "Sangat Dalam":
            return "Potensi Tsunami"
    elif 5.1 <= skala_numerik <= 7.0:
        if jarak == "Dekat" or jarak == "Sedang":
            return "Potensi Tsunami"
    return "Tidak Berpotensi"

# Fungsi untuk menambahkan data ke tabel
def tambah_data(event=None):
    try:
        jarak_input = float(entry_jarak.get())
        kedalaman_input = float(entry_kedalaman.get())
        skala_input = float(entry_skala.get())

        klas_jarak = klasifikasi_jarak(jarak_input)
        klas_kedalaman = klasifikasi_kedalaman(kedalaman_input)
        klas_skala = klasifikasi_skala(skala_input)
        efek = tentukan_efek(klas_jarak, klas_kedalaman, skala_input)

        data_hasil.append({
            "Jarak Dari Pantai": klas_jarak,
            "Kedalaman": klas_kedalaman,
            "Skala": klas_skala,
            "Efek": efek
        })

        # Kosongkan kolom input
        entry_jarak.delete(0, tk.END)
        entry_kedalaman.delete(0, tk.END)
        entry_skala.delete(0, tk.END)
        entry_jarak.focus()  # Fokus ke kolom pertama

        # Update tabel
        update_tabel()
    except ValueError:
        messagebox.showerror("Error", "Pastikan semua input berupa angka!")

def update_tabel():
    for row in tree.get_children():
        tree.delete(row)

    for i, row in enumerate(data_hasil):
        tree.insert("", "end", values=(i + 1, row["Jarak Dari Pantai"], row["Kedalaman"], row["Skala"], row["Efek"]))

# Fungsi untuk mengekspor data ke CSV
def export_csv():
    if not data_hasil:
        messagebox.showwarning("Warning", "Tidak ada data untuk diekspor!")
        return

    # Dapatkan tanggal dan waktu saat ini
    now = datetime.now()
    tanggal = now.strftime("%Y%m%d")
    timestamp = now.strftime("%H%M%S")
    default_filename = f"data_gempa_{tanggal}_{timestamp}.csv"

    # Buka dialog penyimpanan file dengan nama file default
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             initialfile=default_filename,
                                             filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if file_path:
        df = pd.DataFrame(data_hasil)
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Success", f"Data berhasil diekspor ke {file_path}")

# Fungsi untuk mengekspor data ke PDF
def export_pdf():
    if not data_hasil:
        messagebox.showwarning("Warning", "Tidak ada data untuk diekspor!")
        return

    # Dapatkan tanggal dan waktu saat ini
    now = datetime.now()
    tanggal = now.strftime("%Y-%m-%d")
    waktu = now.strftime("%H:%M:%S")
    pengumpulan_ke = len(data_hasil)
    default_filename = f"data_gempa_{now.strftime('%Y%m%d_%H%M%S')}.pdf"

    # Buka dialog penyimpanan file dengan nama file default
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                             initialfile=default_filename,
                                             filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
    if file_path:
        # Buat DataFrame
        df = pd.DataFrame(data_hasil)

        # Konversi DataFrame ke list of lists
        data = [df.columns.to_list()] + df.values.tolist()

        # Buat PDF
        pdf = SimpleDocTemplate(file_path, pagesize=landscape(letter))
        elements = []

        # Setup styles
        styles = getSampleStyleSheet()
        style_normal = styles["Normal"]
        style_heading = styles["Heading1"]

        # Tambahkan keterangan awal
        keterangan = f"""
        <b>Tanggal:</b> {tanggal}<br/>
        <b>Waktu:</b> {waktu}<br/>
        <b>Pengumpulan data ke:</b> {pengumpulan_ke}
        """
        paragraph = Paragraph(keterangan, style_normal)
        elements.append(paragraph)
        elements.append(Spacer(1, 12))  # Tambahkan jarak

        # Tambahkan tabel
        table = Table(data)

        # Tambahkan style ke tabel
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.gray),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ])
        table.setStyle(style)

        # Alternating background colors for rows
        for i in range(1, len(data)):
            if i % 2 == 0:
                bg_color = colors.lightgrey
            else:
                bg_color = colors.beige
            style.add('BACKGROUND', (0,i), (-1,i), bg_color)

        elements.append(table)

        # Bangun PDF
        pdf.build(elements)

        messagebox.showinfo("Success", f"Data berhasil diekspor ke {file_path}")
        os.system("start " + file_path)

# Fungsi untuk memindahkan fokus ke kedalaman
def focus_kedalaman(event):
    entry_kedalaman.focus_set()

# Fungsi untuk memindahkan fokus ke skala
def focus_skala(event):
    entry_skala.focus_set()

# Setup GUI dengan tkinter
data_hasil = []

root = tk.Tk()
root.title("Klasifikasi Gempa dan Tsunami")

# Frame Input
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

# Jarak Dari Pantai
tk.Label(frame_input, text="Jarak Dari Pantai (Km):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
entry_jarak = tk.Entry(frame_input)
entry_jarak.grid(row=0, column=1, padx=5, pady=5)
entry_jarak.bind('<Return>', focus_kedalaman)  # Bind Enter ke fokus kedalaman

# Kedalaman Pusat Gempa
tk.Label(frame_input, text="Kedalaman Pusat Gempa (Km):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
entry_kedalaman = tk.Entry(frame_input)
entry_kedalaman.grid(row=1, column=1, padx=5, pady=5)
entry_kedalaman.bind('<Return>', focus_skala)  # Bind Enter ke fokus skala

# Skala Gempa
tk.Label(frame_input, text="Skala Gempa:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
entry_skala = tk.Entry(frame_input)
entry_skala.grid(row=2, column=1, padx=5, pady=5)
entry_skala.bind('<Return>', tambah_data)  # Bind Enter ke tambah_data

# Tombol Tambah Data
btn_tambah = tk.Button(frame_input, text="Tambah Data", command=tambah_data)
btn_tambah.grid(row=3, column=0, columnspan=2, pady=10)

# Frame Tabel
frame_tabel = tk.Frame(root)
frame_tabel.pack(pady=10)

tree = ttk.Treeview(frame_tabel, columns=("No", "Jarak Dari Pantai", "Kedalaman", "Skala", "Efek"), show="headings")
tree.heading("No", text="No")
tree.heading("Jarak Dari Pantai", text="Jarak Dari Pantai")
tree.heading("Kedalaman", text="Kedalaman")
tree.heading("Skala", text="Skala")
tree.heading("Efek", text="Efek")

tree.column("No", width=50, anchor="center")
tree.column("Jarak Dari Pantai", width=150, anchor="center")
tree.column("Kedalaman", width=150, anchor="center")
tree.column("Skala", width=100, anchor="center")
tree.column("Efek", width=200, anchor="center")

tree.pack()

# Frame Tombol Export
frame_export = tk.Frame(root)
frame_export.pack(pady=10)

btn_export_csv = tk.Button(frame_export, text="Export to CSV", command=export_csv)
btn_export_csv.grid(row=0, column=0, padx=10)

btn_export_pdf = tk.Button(frame_export, text="Export to PDF", command=export_pdf)
btn_export_pdf.grid(row=0, column=1, padx=10)

# Menjalankan GUI
root.mainloop()
