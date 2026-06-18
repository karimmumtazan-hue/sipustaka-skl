# Generated manually from PostgreSQL schema

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Siswa',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nama', models.CharField(max_length=100, blank=True, null=True)),
                ('kelas', models.CharField(max_length=20, blank=True, null=True)),
                ('nis', models.CharField(max_length=20, unique=True, blank=True, null=True)),
                ('is_active', models.BooleanField(blank=True, null=True)),
                ('is_hadir', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'siswa',
            },
        ),

        migrations.CreateModel(
            name='Buku',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('judul', models.CharField(max_length=150, blank=True, null=True)),
                ('pengarang', models.CharField(max_length=100, blank=True, null=True)),
                ('kategori', models.CharField(max_length=100, blank=True, null=True)),
                ('penerbit', models.CharField(max_length=100, blank=True, null=True)),
                ('tahun_terbit', models.IntegerField(blank=True, null=True)),
                ('rak', models.CharField(max_length=50, blank=True, null=True)),
                ('stok', models.IntegerField(blank=True, null=True)),
                ('deskripsi', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'buku',
            },
        ),

        migrations.CreateModel(
            name='Peminjaman',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tanggal_pinjam', models.DateField(blank=True, null=True)),
                ('jatuh_tempo', models.DateField(blank=True, null=True)),
                ('keperluan', models.TextField(blank=True, null=True)),
                ('status', models.CharField(max_length=50, blank=True, null=True)),
                (
                    'buku',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.CASCADE,
                        to='perpustakaan.buku',
                    ),
                ),
                (
                    'siswa',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.CASCADE,
                        to='perpustakaan.siswa',
                    ),
                ),
            ],
            options={
                'db_table': 'peminjaman',
            },
        ),
    ]