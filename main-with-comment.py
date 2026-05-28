
# pyqt6 dinggo load folder ui
from __future__ import annotations

import sys
from pathlib import Path

from PyQt6 import uic
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,
)


BASE_DIR = Path(__file__).resolve().parent
UI_PATH = BASE_DIR / "ui" / "inventaris.ui"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "inventaris.sqlite"


LOGIN_PATH = BASE_DIR / "ui" / "p.ui" # Lokasi Folder ui Login App

# Ui Login APP
class LoginApp(QMainWindow):
    """Aplikasi CRUD sederhana untuk materi Form dan Database PyQt6."""

# init
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(str(LOGIN_PATH), self) # Ngambil Ui login di folder ui
        self.loginButton.clicked.connect(self.handle_login) # Ngambil tombol udah di klik belum
    

   
    def handle_login(self) -> None:
        username = self.usernameInput.text() # ambil isi username
        password = self.passwordInput.text() # ambil isi password
        if not username or not password: # kalau input kosong
            print("Isi username dan password") # tampilkan pesan
            return
        
        # Nek password bener
        if username == "admin" and password == "admin tak parani":
            self.main_window = InventarisBukuApp() # inisialisasi
            self.main_window.show() # Tampilkan Ui Utama
            return

# Nek Password Salah
        else:
            print("login gagal psht siap marani") # terminal

      
        
    



# dinggo load folder ui inventaris buku
class InventarisBukuApp(QMainWindow):
    """Aplikasi CRUD sederhana untuk materi Form dan Database PyQt6."""

# 
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(str(UI_PATH), self)

        self.selected_id: int | None = None
        self.db = self._open_database() # Gawe file sqlite neng jero folder data

# ngambil data di folder data / sqlite
        self._setup_widgets() 
        self._create_table()
        self._seed_sample_data()
        self._connect_signals()
        self.load_data()

    
    def _open_inventory(self) -> None:
       self.main_window = InventarisBukuApp()
       self.main_window.show()
       self.close()


    def _open_database(self) -> QSqlDatabase:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(str(DB_PATH))
        if not db.open():
            QMessageBox.critical(
                self,
                "Database Error",
                "Database tidak dapat dibuka. Periksa folder data aplikasi.",
            )
            sys.exit(1)
        return db

    def _setup_widgets(self) -> None:
        self.setWindowTitle("Inventaris Buku Mini - CRUD PyQt6")

        self.cmbKategori.clear()
        self.cmbKategori.addItems(
            [
                "Buku Kuliah",
                "Buku Praktikum",
                "Referensi",
                "Majalah/Jurnal",
                "Lainnya",
            ]
        )

        self.spnStok.setMinimum(0)
        self.spnStok.setMaximum(9999)
        self.dtMasuk.setDate(QDate.currentDate())
        self.dtMasuk.setCalendarPopup(True)

        headers = ["ID", "Kode", "Judul", "Kategori", "Stok", "Lokasi", "Tanggal Masuk"]
        self.tblBuku.setColumnCount(len(headers))
        self.tblBuku.setHorizontalHeaderLabels(headers)
        self.tblBuku.setColumnHidden(0, True)
        self.tblBuku.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblBuku.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tblBuku.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblBuku.horizontalHeader().setStretchLastSection(True)

        self.lblStatus.setText("Siap. Tambahkan data buku pertama.")
        self.lblTotalStok.setText("Total stok: 0")

    def _connect_signals(self) -> None:
        self.btnSimpan.clicked.connect(self.tambah_buku)
        self.btnUbah.clicked.connect(self.ubah_buku)
        self.btnHapus.clicked.connect(self.hapus_buku)
        self.btnBersihkan.clicked.connect(self.bersihkan_form)
        self.btnCari.clicked.connect(self.cari_data)
        self.btnResetCari.clicked.connect(self.reset_filter)
        self.txtCari.returnPressed.connect(self.cari_data)
        self.tblBuku.itemSelectionChanged.connect(self.pilih_baris)

    def _create_table(self) -> None:
        query = QSqlQuery(self.db)
        ok = query.exec(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode TEXT NOT NULL UNIQUE,
                judul TEXT NOT NULL,
                kategori TEXT NOT NULL,
                stok INTEGER NOT NULL DEFAULT 0,
                lokasi TEXT NOT NULL,
                tanggal_masuk TEXT NOT NULL
            )
            """
        )
        if not ok:
            self._show_db_error(query, "Tabel books gagal dibuat.")

    def _seed_sample_data(self) -> None:
        count_query = QSqlQuery(self.db)
        count_query.exec("SELECT COUNT(*) FROM books")
        if count_query.next() and count_query.value(0) > 0:
            return

        samples = [
            ("B001", "PBO Dasar", "Buku Kuliah", 12, "Rak A1", "2026-05-19"),
            ("B002", "Python GUI", "Buku Praktikum", 7, "Rak B2", "2026-05-19")
              ("B003", "Suki Liar", "Buku Praktikum", 7, "Rak B2", "2026-05-19"),
        ]
        for row in samples:
            query = QSqlQuery(self.db)
            query.prepare(
                """
                INSERT INTO books (kode, judul, kategori, stok, lokasi, tanggal_masuk)
                VALUES (?, ?, ?, ?, ?, ?)
                """
            )
            for index, value in enumerate(row):
                query.bindValue(index, value)
            query.exec()

    def _read_form(self) -> dict[str, object] | None:
        kode = self.txtKode.text().strip().upper()
        judul = self.txtJudul.text().strip()
        kategori = self.cmbKategori.currentText().strip()
        stok = int(self.spnStok.value())
        lokasi = self.txtLokasi.text().strip()
        tanggal_masuk = self.dtMasuk.date().toString("yyyy-MM-dd")

        if not kode:
            QMessageBox.warning(self, "Validasi", "Kode buku wajib diisi.")
            self.txtKode.setFocus()
            return None
        if not judul:
            QMessageBox.warning(self, "Validasi", "Judul buku wajib diisi.")
            self.txtJudul.setFocus()
            return None
        if not lokasi:
            QMessageBox.warning(self, "Validasi", "Lokasi/rak buku wajib diisi.")
            self.txtLokasi.setFocus()
            return None

        return {
            "kode": kode,
            "judul": judul,
            "kategori": kategori,
            "stok": stok,
            "lokasi": lokasi,
            "tanggal_masuk": tanggal_masuk,
        }

    def tambah_buku(self) -> None:
        data = self._read_form()
        if data is None:
            return

        query = QSqlQuery(self.db)
        query.prepare(
            """
            INSERT INTO books (kode, judul, kategori, stok, lokasi, tanggal_masuk)
            VALUES (?, ?, ?, ?, ?, ?)
            """
        )
        self._bind_book_values(query, data)

        if not query.exec():
            self._show_db_error(query, "Data gagal ditambahkan. Kode buku mungkin sudah dipakai.")
            return

        self.load_data()
        self.bersihkan_form()
        self.lblStatus.setText(f"Buku {data['kode']} berhasil ditambahkan.")
        QMessageBox.information(self, "Berhasil", "Data buku berhasil ditambahkan.")

# dinggo load data ning tabel
    def load_data(self, keyword: str = "") -> None:
        query = QSqlQuery(self.db)
        if keyword:
            query.prepare(
                """
                SELECT id, kode, judul, kategori, stok, lokasi, tanggal_masuk
                FROM books
                WHERE kode LIKE ?
                   OR judul LIKE ?
                   OR kategori LIKE ?
                   OR lokasi LIKE ?
                ORDER BY judul
                """
            )
            pattern = f"%{keyword}%"
            for index in range(4):
                query.bindValue(index, pattern)
        else:
            query.prepare(
                """
                SELECT id, kode, judul, kategori, stok, lokasi, tanggal_masuk
                FROM books
                ORDER BY judul
                """
            )

        if not query.exec():
            self._show_db_error(query, "Data gagal dibaca dari database.")
            return

        self.tblBuku.setRowCount(0)
        while query.next():
            row = self.tblBuku.rowCount()
            self.tblBuku.insertRow(row)
            for col in range(7):
                item = QTableWidgetItem(str(query.value(col)))
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                if col == 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.tblBuku.setItem(row, col, item)

        self.tblBuku.resizeColumnsToContents()
        self._update_total_stok()
        self.lblStatus.setText(f"{self.tblBuku.rowCount()} data tampil di tabel.")

# dinggo fungsi milih baris
    def pilih_baris(self) -> None:
        selected_items = self.tblBuku.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        self.selected_id = int(self.tblBuku.item(row, 0).text())
        self.txtKode.setText(self.tblBuku.item(row, 1).text())
        self.txtJudul.setText(self.tblBuku.item(row, 2).text())
        self.cmbKategori.setCurrentText(self.tblBuku.item(row, 3).text())
        self.spnStok.setValue(int(self.tblBuku.item(row, 4).text()))
        self.txtLokasi.setText(self.tblBuku.item(row, 5).text())
        self.dtMasuk.setDate(QDate.fromString(self.tblBuku.item(row, 6).text(), "yyyy-MM-dd"))
        self.lblStatus.setText(f"Data ID {self.selected_id} dipilih. Siap diubah atau dihapus.")

# dinggo fungsi ubah data
    def ubah_buku(self) -> None:
        if self.selected_id is None:
            QMessageBox.warning(self, "Pilih Data", "Pilih satu baris data sebelum menekan tombol Ubah.")
            return

        data = self._read_form()
        if data is None:
            return

        query = QSqlQuery(self.db)
        query.prepare(
            """
            UPDATE books
            SET kode = ?, judul = ?, kategori = ?, stok = ?, lokasi = ?, tanggal_masuk = ?
            WHERE id = ?
            """
        )
        self._bind_book_values(query, data)
        query.bindValue(6, self.selected_id)

        if not query.exec():
            self._show_db_error(query, "Data gagal diubah. Kode buku mungkin bentrok dengan data lain.")
            return

        self.load_data(self.txtCari.text().strip())
        self.bersihkan_form()
        self.lblStatus.setText(f"Buku {data['kode']} berhasil diubah.")
        QMessageBox.information(self, "Berhasil", "Data buku berhasil diubah.")

# ubah buku
    def hapus_buku(self) -> None:
        if self.selected_id is None:
            QMessageBox.warning(self, "Pilih Data", "Pilih satu baris data sebelum menekan tombol Hapus.")
            return

        kode = self.txtKode.text().strip()
        confirm = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Yakin ingin menghapus buku {kode}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        query = QSqlQuery(self.db)
        query.prepare("DELETE FROM books WHERE id = ?")
        query.bindValue(0, self.selected_id)

        if not query.exec():
            self._show_db_error(query, "Data gagal dihapus.")
            return

        self.load_data(self.txtCari.text().strip())
        self.bersihkan_form()
        self.lblStatus.setText(f"Buku {kode} berhasil dihapus.")
        QMessageBox.information(self, "Berhasil", "Data buku berhasil dihapus.")

# dinggo fungsi cari data
    def cari_data(self) -> None:
        keyword = self.txtCari.text().strip()
        self.load_data(keyword)
        if keyword:
            self.lblStatus.setText(f"Hasil pencarian untuk: {keyword}")

    def reset_filter(self) -> None:
        self.txtCari.clear()
        self.load_data()

# bersihkan form
    def bersihkan_form(self) -> None:
        self.selected_id = None
        self.txtKode.clear()
        self.txtJudul.clear()
        self.cmbKategori.setCurrentIndex(0)
        self.spnStok.setValue(0)
        self.txtLokasi.clear()
        self.dtMasuk.setDate(QDate.currentDate())
        self.tblBuku.clearSelection()
        self.txtKode.setFocus()



    def _bind_book_values(self, query: QSqlQuery, data: dict[str, object]) -> None:
        query.bindValue(0, data["kode"])
        query.bindValue(1, data["judul"])
        query.bindValue(2, data["kategori"])
        query.bindValue(3, data["stok"])
        query.bindValue(4, data["lokasi"])
        query.bindValue(5, data["tanggal_masuk"])

    def _update_total_stok(self) -> None:
        total = 0
        for row in range(self.tblBuku.rowCount()):
            item = self.tblBuku.item(row, 4)
            if item is not None:
                total += int(item.text())
        self.lblTotalStok.setText(f"Total stok tampil: {total}")

    def _show_db_error(self, query: QSqlQuery, message: str) -> None:
        detail = query.lastError().text()
        self.lblStatus.setText(message)
        QMessageBox.warning(self, "Database", f"{message}\n\nDetail: {detail}")

# Close database sql dari file
    def closeEvent(self, event) -> None:  
        if self.db.isOpen():
            self.db.close() # buat close file sqlite dari data
        super().closeEvent(event) # Nggo nutup software ben bener logic e

# fungsi main kalok pertama kali jalanin file
def main() -> None:
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec())




# Jalanke fungsi iki
if __name__ == "__main__":
    main()
