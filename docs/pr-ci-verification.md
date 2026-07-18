# Pull Request CI Verification

This marker exists to trigger and verify the pull-request path of the `Toolkit CI` workflow before publishing `v0.1.0`.

Verification scope:

- install the package;
- run the unit tests;
- execute the installed `witrt` CLI;
- generate and validate the example Markdown report;
- upload the report artifact.
