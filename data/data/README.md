Sample History Dataset Documentation

Nature of the Dataset
The file demo_vehicle_history.json inside this directory is a synthetic demonstration dataset. It contains artificial structural validation entries generated solely to test data-handling infrastructure, cross-reference loops, score calculations, and multi-column tables without storing or processing protected consumer data.

Schema Architecture and Parameters
- vin: The unique 17-character sequence used to track the target vehicle asset.
- data_type: Static indicator set to "demo" across records to clarify data classification.
- source_label: Provenance marker set to "Demo dataset" to maintain data transparency.
- imported_from_country_demo: Origin tracker showing the country from which the vehicle was shipped.
- auction_price_demo: Mock financial transaction price recorded during wholesale clearing.
- salvage_flag_demo: Safety tracking indicator where 1 represents a historical total loss write-off and 0 represents a clear status.
- accident_count_demo: Numeric value tracking historical collision counts recorded for the vehicle.

Legal and Architectural Boundaries
Comprehensive vehicle history records, vehicle ownership title transfers, and insurance total loss logs are protected inside premium, paid commercial networks. Because free public endpoints to look up historical vehicle damage do not exist on the open web, this prototype utilizes a localized demonstration file to securely verify risk scoring rules while satisfying project evaluation requirements.

Operational Standards
- Mathematical constraints adhere to federal Modulus-11 check-digit verification formulas.
- Layout architectures map to simple data tables for clear grading visibility.