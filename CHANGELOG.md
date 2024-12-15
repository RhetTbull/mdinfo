# Changelog

All notable changes to this project will be documented in this file.

## Python 3.13 Support

[v0.2.0](https://github.com/RhetTbull/mdinfo/releases/tag/v0.2.0)

### 14 December 2024

### Synopsis

Support for Python 3.13 has been added.
i
## Combine operator

[v0.1.3](https://github.com/RhetTbull/mdinfo/releases/tag/v0.1.3)

### 24 March 2024

### Synopsis

"pretext{delim+template_field:subfield|filter[find,replace]conditional&combine_value?bool_value,default}posttext"

&combine_value: Template fields may be combined with another template statement
to return multiple values. The combine_value is another template statement. For
example, the template {created.year&{audio:title,}} would resolve to ["1999",
"The Title"] if the file was created in 1999 and had the title "The Title".
Because the combine_value is a template statement, multiple templates may be
combined together by nesting the combine operator:
{template1&{template2&{template3,},},}. In this example, a null default value is
used to prevent the default value from being combined if any of the nested
templates does not resolve to a value.

### Added

- Added combine operator (&) to combine two templates (results in multi-value template)


## Plugins!

[v0.1.1](https://github.com/RhetTbull/mdinfo/releases/tag/v0.1.1)

### 19 March 2023

### Added

- Added plugins: mdinfo-exiftool, mdinfo-macos

## Initial Release

[v0.1.0](https://github.com/RhetTbull/mdinfo/releases/tag/v0.1.0)

### 18 March 2023

- Initial release of the project.
