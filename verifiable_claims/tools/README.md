# Tools

Tools for designing certificate templates, instantiating a certificate batch, and import/export tasks

see example of certificate template and batch creation in sample_data 


### Adding custom fields

You can specify additional global fields (fields that apply for every certificate in the batch) and additional per-recipient fields (fields that you will specify per-recipient).

#### Important: defining your custom fields in a JSON-LD context
When adding either global or per-recipient custom fields, you must define each of your new terms in a [JSON-LD context](https://json-ld.org/spec/latest/json-ld/). You can either point to an existing JSON-LD context, or embed them directly in the context of the certificate. For an example of the latter, see the [JSON-LD specification section 3.1](https://json-ld.org/spec/latest/json-ld/#the-context). In this case, the `@context` value would be an array listing the existing context links, and your new definition.

Examples of both options are below:
```
{
  "@context": [
        "https://w3id.org/openbadges/v2",
        "https://w3id.org/blockcerts/v2",
        "https://your-custom-context/v1",                                <-- option 1: point to custom JSON-LD context
        {                                                                <-- option 2: directly embed in certificate
             "xyz_custom_field": "http://path/to/xyz_custom_field",
              ... // and all other custom fields
        }
    ]
}
```

#### Custom global fields

You can specify custom global fields in the conf.ini file with the `additional_global_fields` entry

For each additional global field, you must indicate:

- the jsonpath to the field
- the global value to use

Example:

conf.ini:
```
additional_global_fields = {"fields": [{"path": "$.certificate.subtitle","value": "custom subtitle"}]}
```

or, expanded for readability:
```
    additional_global_fields = {
        "fields": 
            [
                {
                    "path": "$.certificate.subtitle",
                    "value": "custom subtitle"
                }
            ]
    }

```

#### Custom per-recipient fields

See above note on (current) manual step of defining custom JSON-LD context.


For each additional per-recipient field, you must indicate the following in the `additional_per_recipient_fields` config field:

- the jsonpath to the field
- the merge_tag placeholder to use
- the csv column where the value (per recipient) can be found. This is used by instantiate_certificate_batch

Example:

conf.ini version:
```
    additional_per_recipient_fields = {"fields": [{"path": "$.xyz_custom_field","value": "*|THIS WILL CONTAIN XYZ CUSTOM VALUES|*","csv_column": "xyz_custom_field"}]}
```