# Shipping

Shipping providers are intentionally isolated from search results. A provider must return a verified quote for the destination CEP; the application never invents a freight value.

`ignore_shipping=True` is available for marketplace list-building flows where the user explicitly wants to compare products without freight.
