# MCP Protocol Kuralları

- Tool metodları çağrı sonuçlarında her zaman content listesi ile basar.
- JSON formatı tercih edilmeli, result dict halinde `ensure_ascii=False` json dump atılmalıdır.
- Hatalar için response nesnesinde `isError=True` setlenmelidir.
