# SION-ATK-CLOUD <!-- omit in toc -->
Sebuah kumpulan skrip yang dibuat dengan tujuan bruteforce nim dan password mahasiswa stikom-bali.ac.id.

Ketika pertama kali dipergunakan author berhasil mendapatkan nim dan password yang terdapat di folder found, namun setelah tanggal 10 Juni 2019 setiap mahasiswa diwajibkan untuk mengganti password diantara 8-12 karakter, sehingga skrip ini sudah tidak bisa dipergunakan.

## Table of  <!-- omit in toc -->
- [SAgent](#SAgent)
- [SDict](#SDict)
- [STract](#STract)
- [SLogin](#SLogin)
- [ELogin](#ELogin)
- [SBrute](#SBrute)
  - [example](#example)


## SAgent
Modul untuk generator untuk menghasilkan user-agent dari berbagai sumber browser, dependency dari modul Login
## SDict
Modul untuk generator dictionary yang digunakan oleh modul Login
## STract
Modul ini berfungsi mengekstrak nama dan nim dari semua mahasiswa aktif
## SLogin
Modul untuk melakukan login ke web sion.stikom-bali.ac.id
## ELogin
Modul untuk melakukan login ke web elearning.stikom-bali.ac.id
## SBrute
Modul utama untuk melakukan bruteforce, untuk jenis-jenis argument yang bisa digunakan silahkan cek script dari modul yang bersangkutan.
### example
`python3 __main__.py -T 8 --infile temp.txt --disable-console-logging`