---
description: PyPI Yayınlama Adımları
---

1. pyproject.toml bağımlılık ve versiyon bilgisini gözden geçir.
2. Geriye yönelik testleri, mock bazlı pass edildiğinden emin ol.
3. GitHub 'main' alanını yayınla ve tag (örn v1.0.0) oluştur.
4. Tag trigger ile github workflow tetiklensin (`publish.yml`).
5. Alternatif repository platformlarına (Smithery) ekleme yap.
