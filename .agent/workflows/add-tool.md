---
description: MCP Araç Ekleme Adımları
---

1. client.py içine ilgili client veya external api logic metodunu ekle.
2. test_server.py içerisinde mock'u ve tool testini oluştur.
3. server.py içerisinde hem `list_tools`, hem de `call_tool` handler bloklarını genişlet.
4. Terminal ile testleri `pytest` vasıtasıyla kontrol ederek güvenliği teyit et.
