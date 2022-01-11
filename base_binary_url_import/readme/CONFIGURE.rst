Configuration shouldn't be needed, however you can customize the import using
following `ir.config_parameter`:

* `binary.url.import.max.size`: Maximum size (in Bytes) of imported Binaries.
  (default = 10485760 = 10MB)

* `binary.url.import.timeout`: Timeout limit (in seconds) for HTTP requests to
  get an answer.
  (default = 5)
