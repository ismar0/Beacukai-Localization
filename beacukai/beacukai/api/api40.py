import frappe
from frappe import _
from frappe.utils import formatdate

@frappe.whitelist()
def export_dokumen_pabean(name):
    doc = frappe.get_doc("Dokumen Pabean", name)
    settings = frappe.get_single("CEISA Settings")

    # # Helper untuk ambil child table dan konversi ke dict
    # def get_children(doctype, parentfield):
    #     children = doc.get(parentfield)
    #     return [d.as_dict() for d in children] if children else []

    # Ambil entitas dan format tanggal
    entitas_list = frappe.get_all(
        "Entitas",
        filters={"parent": doc.name},
        fields=[
            "alamat_entitas as alamatEntitas",
            "jenis_entitas as kodeEntitas",
            "kode_jenis_identitas as kodeJenisIdentitas",
            "nama_entitas as namaEntitas",
            "nib as nibEntitas",
            "nomor_identitas as nomorIdentitas",
            "no_ijin_entitas as nomorIjinEntitas",
            "kode_jenis_api as kodeJenisApi",
            "seri_entitas as seriEntitas",
            "tanggal_ijin_entitas as tanggalIjinEntitas"
        ],
        order_by="seri_entitas asc"
    )

    for e in entitas_list:
        if e.get("tanggalIjinEntitas"):
            e["tanggalIjinEntitas"] = formatdate(e["tanggalIjinEntitas"], "yyyy-mm-dd")

        if not e.get("nibEntitas"):
            e["nibEntitas"] = ""

        if not e.get("kodeJenisApi"):
            e["kodeJenisApi"] = ""

    # Ambil dokumen dan format tanggal
    dokumen_list = frappe.get_all(
        "Dokumen",
        filters={"parent": doc.name},
        fields=[
            "jenis_dokumen as kodeDokumen",
            "nomor_dokumen as nomorDokumen",
            "seri_dokumen as seriDokumen",
            "tanggal_dokumen as tanggalDokumen"
        ],
        order_by="seri_dokumen asc"
    )

    for e in dokumen_list:
        if e.get("tanggal_dokumen"):
            e["tanggal_dokumen"] = formatdate(e["tanggal_dokumen"], "yyyy-mm-dd")

    # Ambil pengangkut dan format tanggal
    pengangkut_list = frappe.get_all(
        "Pengangkut",
        filters={"parent": doc.name},
        fields=[
            "nama_pengangkut as namaPengangkut",
            "nomor_pengangkut as nomorPengangkut",
            "seri_pengangkut as seriPengangkut"
        ],
        order_by="seri_pengangkut asc"
    )

    # Ambil kemasan dan format tanggal
    kemasan_list = frappe.get_all(
        "Kemasan",
        filters={"parent": doc.name},
        fields=[
            "jumlah_kemasan as jumlahKemasan",
            "kode_kemasan as kodeJenisKemasan",
            "merek as merkKemasan",
            "seri_kemasan as seriKemasan"
        ],
        order_by="seri_kemasan asc"
    )

    # Ubah merek null jadi ""
    for k in kemasan_list:
        if not k.get("merkKemasan"):
            k["merkKemasan"] = ""

    # Ambil pungutan dan format tanggal
    pungutan_list = frappe.get_all(
        "Pungutan",
        filters={"parent": doc.name},
        fields=[
            "kode_fasilitas_tarif as kodeFasilitasTarif",
            "kode_jenis_pungutan as kodeJenisPungutan",
            "nilai_pungutan as nilaiPungutan"
        ]
    )

    result = {
        "asalData": "S",
        "asuransi": 0.0,
        "bruto": doc.bruto or 0.0000,
        "cif": 0.0,
        "kodeJenisTpb": doc.jenis_tpb,
        "freight": 0.0,
        "hargaPenyerahan": doc.harga_penyerahan or 0.00,
        "idPengguna": f"{settings.nib} {settings.npwp}",
        "jabatanTtd": doc.jabatan_pernytaan,
        "jumlahKontainer": 0,  # Optional: bisa len(doc.kontainer) atau frappe.db.count("Kontainer", {"parent": doc.name})
        "kodeDokumen": doc.bctype,
        "kodeKantor": doc.kantor_pabean,
        "kodeTujuanPengiriman": doc.tujuan_pengiriman,
        "kotaTtd": doc.kota_pernyataan,
        "namaTtd": doc.nama_pernyataan,
        "netto": doc.netto or 0.0000,
        "nik": settings.npwp,
        "nomorAju": doc.nomor_aju,
        "seri": 0,
        "tanggalAju": formatdate(doc.tanggal_aju, "yyyy-mm-dd"),
        "tanggalTtd": formatdate(doc.tanggal_pernyataan, "yyyy-mm-dd"),
        "volume": doc.volume or 0.0000,
        "biayaTambahan": 0.00,
        "biayaPengurang": doc.biaya_pengurang or 0.00,
        "vd": 0.00,
        "uangMuka": doc.uang_muka or 0.00,
        "nilaiJasa": doc.nilai_jasa or 0.00,
        "entitas": entitas_list,
        "dokumen": dokumen_list,
        "pengangkut": pengangkut_list,
        "kontainer": [],
        "kemasan": kemasan_list,
        "pungutan": pungutan_list,
        "barang": [],
    }

    for b in frappe.get_all("Barang", filters={"dokumen_pabean": doc.name}, fields=["*"]):
        barang = {
            "asuransi": 0.00,
            "bruto": 0.0000,
            "cif": 0.00,
            "diskon": b.diskon or 0.00,
            "hargaEkspor": 0.00,
            "hargaPenyerahan": b.harga_penyerahan,
            "hargaSatuan": 0.00,
            "isiPerKemasan": 0,
            "jumlahKemasan": b.jumlah_kemasan,
            "jumlahRealisasi": 0.00,
            "jumlahSatuan": b.jumlah,
            "kodeBarang": b.kode_barang,
            "kodeDokumen": "40",
            "kodeJenisKemasan": b.jenis_kemasan,
            "kodeSatuanBarang": b.kode_satuan_barang,
            "merk": b.merk or "-",
            "netto": b.netto,
            "nilaiBarang": 0.00,
            "posTarif": b.hscode,
            "seriBarang": b.seri_barang,
            "spesifikasiLain": b.spesifikasi_lain or "-",
            "tipe": b.tipe or "-",
            "ukuran": b.ukuran or "-",
            "uraian": b.uraian_barang,
            "volume": 0.0000,
            "cifRupiah": 0.00,
            "hargaPerolehan": 0.00,
            "ndpbm": 0.00,
            "uangMuka": 0.00,
            "nilaiJasa": b.nilai_jasa or 0.00,
        }

        barang["barangTarif"] = frappe.get_all("Barang Tarif", filters={"parent": b.name}, fields=[
            "kode_tarif as kodeJenisTarif",
            "jumlah_satuan as jumlahSatuan",
            "kode_fasilitas as kodeFasilitasTarif",
            "kode_satuan as kodeSatuanBarang",
            "nilai_bayar as nilaiBayar",
            "nilai_fasilitas as nilaiFasilitas",
            "nilai_sudah_di_lunasi as nilaiSudahDilunasi",
            "seri_barang as seriBarang",
            "tarif",
            "tarif_fasilitas as tarifFasilitas",
            "kode_pungutan as kodeJenisPungutan"
        ])

        result["barang"].append(barang)

    return result
