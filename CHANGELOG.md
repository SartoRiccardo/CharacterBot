# ChangeLog

## 1.0.0 - 2018-09-19

### Added
+ Prefix is now customizable with `prefix (newprefix)`
+ Added `download` command
+ You can now import/export files using `import` and `download`
+ Added ChangeLog
+ Bot deletes all the server's data when it leaves the server

### Changed
+ Default prefix changed to `$`
+ `help` command uses reactions to cycle through pages
+ Server specific data such as the prefix is now stored in a Postgres table instead of a JSON file
+ Removed useless functions

### Fixed
+ `add` doesn't suggest camel case names anymore
+ `import` now reliably gets the table name

## 0.10.1 - 2018-09-18

### Fixed
+ Fixed typos in `info` and `share` commands that caused them to not work

## 0.10.0 - 2018-09-19

### Changed
+ Completely refactored commands, now it's all cleaner and uses extensions
+ Help command is now an embed
+ Got rid of the `char` prefix, now instead of doing `>>char (command)` you just do `>>(command)`
+ You can now see if some characters are taken directly with `list`

### Fixed
+ Fixed bug where it wouldn't update any data if a user changed name

