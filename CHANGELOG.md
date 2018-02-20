# CHANGELOG

To find the version running on your machine use the command `topicexplorer version`. In older releases, this was `vsm version` or `vsm --version`.

Not all beta releases are documented below. We give the summary of all changes between major stable milestones. If you are using a beta version not listed below, we highly recommend switching to one listed below or simply updating using `topicexplorer update`.

This project follows the [PEP 440](https://www.python.org/dev/peps/pep-0440/) versioning conventions. See [Semantic Versioning](http://semver.org/) for justification. The only difference between PEP 440 and SemVer.org is the pre-release format **1.0b20** vs. 1.0-beta.20.

This CHANGELOG follows the conventions at [Keep a CHANGELOG](http://keepachangelog.com/). Versions should group changes in the order: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, and `Security` (see section ["What makes a good change log?"](http://keepachangelog.com/)).

## Unreleased

## [1.0b182] - 2017-10-08
- Added:
  - [#200](https://github.com/inpho/topic-explorer/issues/200) Python 3 Support
  - Added support for the [htrc-feature-reader](https://github.com/htrc/htrc-feature-reader).
  - Added `topicexplorer export` and `topicexplorer import` commands.
- Changed:
  - [#213](https://github.com/inpho/topic-explorer/issues/213) demo launches to browser
  - [#210](https://github.com/inpho/topic-explorer/issues/210) isomap axis removed
  - [#206](https://github.com/inpho/topic-explorer/issues/206) docs.json file very large, causes slow performance. Now defaults to 10 results
- Fixed: 
  - [#218](https://github.com/inpho/topic-explorer/issues/218) Python 3: raw hex in prep frequency lists
  - [#217](https://github.com/inpho/topic-explorer/issues/217) Python 3: init frequency filter b'string'
  - [#216](https://github.com/inpho/topic-explorer/issues/216) demo/fulltext not working / Python 3
  - [#215](https://github.com/inpho/topic-explorer/issues/215) ap.md not updating on Windows
  - [#211](https://github.com/inpho/topic-explorer/issues/211) Bad link to Blei 2003 in AP demo
  - [#208](https://github.com/inpho/topic-explorer/issues/208) UnicodeEncodeError when click on fulltext icon
  - [#207](https://github.com/inpho/topic-explorer/issues/207) Python 3 error in `topicexplorer update`
  - [#205](https://github.com/inpho/topic-explorer/issues/205) Mac OS Update has broken launch to browser (and Jupyter)
  - [#204](https://github.com/inpho/topic-explorer/issues/204) ignore .DS_Store files on Mac
  - [#203](https://github.com/inpho/topic-explorer/issues/203) Python 3 install_data error
  - [#202](https://github.com/inpho/topic-explorer/issues/202) Unicode errors on combined 2+3 codebase during prep stage.
  - [#194](https://github.com/inpho/topic-explorer/issues/202) Demo issue running within conda env

## [1.0b159] - 2017-04-26
- Added:
  - Support for custom index.html in app.wsgi multi-model Apache config.
- Changed:
  - Isomap now exmaines more nearest neighbors, which leads to lower numbers of overlapping topics in cluster view.
- Fixed:
  - [#199](https://github.com/inpho/topic-explorer/issues/199) warn user when term is not in corpus
  - [#198](https://github.com/inpho/topic-explorer/issues/198) uBlock Origin blocks `fingerprint.js` from loading, preventing document search
  - [#187](https://github.com/inpho/topic-explorer/issues/187) true button in handian document modals
  - [#184](https://github.com/inpho/topic-explorer/issues/184) longer texts are not scrollable
  - [#183](https://github.com/inpho/topic-explorer/issues/183) init is not selecting correct corpus structure when exclude files are present
  - Issue with decoding unicode URL parameters

## [1.0b146] - 2016-11-22
- Added:
  - [#144](https://github.com/inpho/topic-explorer/issues/144) permissions string - modal now accessible via © button in lower left.
  - Sidebar is now on all subpages.
  - Topic Fingerprint view now available via the Document view page.
- Changed:
  - All pages now load from a single `master.mustache.html` filled in with the appropriate subpage.
  - Upgraded all sites to Bootstrap 3.
- Fixed:
  - `topicexplorer demo` now has a corpus description.
  - [#177](https://github.com/inpho/topic-explorer/issues/177) 1.04b145 unpickling error
  - [#172](https://github.com/inpho/topic-explorer/issues/172) unicode error with metadata import
  - [#171](https://github.com/inpho/topic-explorer/issues/171) term search for topics internal server error
  - [#169](https://github.com/inpho/topic-explorer/issues/169) directory structure error during init
  - [#104](https://github.com/inpho/topic-explorer/issues/104) Metadata import 
  - Variety of rendering errors in the Document-view page.
  - Fixed issue with histogram bar width

## [1.0b134] - 2016-10-09
- Added:
  - documentation for BibTeX support.
  - [#153](https://github.com/inpho/topic-explorer/issues/153) Add default index.html
  - [#143](https://github.com/inpho/topic-explorer/issues/143) Links to corpus home page
  - [#99](https://github.com/inpho/topic-explorer/issues/99) Add `-q` to all commands to run without prompts
- Changed:
  - [#154](https://github.com/inpho/topic-explorer/issues/154) Modal fulltext default
  - [#120](https://github.com/inpho/topic-explorer/issues/120) "continue training" is ambiguous
  - Updated `vsm` to `0.4.0b6`
- Fixed:
  - Metadata now keeps all information in unicode.
  - `topicexplorer metadata` now allows for label updates with `--rename` flag.
  - Upgrade to D3 for topic cluster display broke other parts of visualization. Reverted D3 and removed chargeDistance property from cluster view.
  - [#168](https://github.com/inpho/topic-explorer/issues/168) Corpus rebuild prompt does not work correctly.
  - [#166](https://github.com/inpho/topic-explorer/issues/166) Invalid attribute 'quiet'?
  - [#165](https://github.com/inpho/topic-explorer/issues/165) Continue training does not remove old clusters
  - [#163](https://github.com/inpho/topic-explorer/issues/163) Continue training does not update model_pattern

## [1.0b121] - 2016-09-18
- Added:
  - topic cluster display
- Fixed:
  - [#160](https://github.com/inpho/topic-explorer/issues/160) - New isomap display doesn't load in Safari
  - Page labels in HTRC extension
  - BibTeX extension config file loading
  - `topicexplorer metadata` now works with all context types

## [1.0b111] - 2016-08-14
- Added:
  - `topicexplorer metadata` command with list, export, and import
- Changed:
  - Ran `autopep8` on `topicexplorer`, `topicexplorer.extensions` and `topicexplorer.lib`
- Removed:
  - Dependency for `pyenchant`.
- Fixed:
  - Duplicate topics (fixed via `vsm==0.4.0b4` regression)
  - Error in topic view due to uncast float.

## [1.0b107] - 2016-07-30
- Added:
  - mod_wsgi support
- Removed:
  - Module `topicexplorer.launch`. Alias for command `topicexplorer launch` still works and is documented way to launch browser. Reserve `topicexplorer serve` for advanced use.
- Fixed:
  - [#37](http://github.com/inpho/topic-explorer/issues/37) - Merge ports to single in-page model switch

## [1.0b106] - 2016-07-25
- Added:
  - New tutorial notebook.
  - Mendeley support via BibTeX export (undocumented).
  - Chinese language support using [pymmseg segmenter](https://pypi.python.org/pypi/pymmseg):
    - Modern Chinese (Mandarin): `topicexplorer init --tokenizer zh`
    - Classical Chinese: `topicexplorer init --tokenizer ltc`
    - Classical Chinese (alias): `topicexplorer init --tokenizer och`
  - Support for hard-coded phrasal tokenizers, should inspire generic SKOS tokenizers:
    - [InPhO ontology](https://inpho.cogs.indiana.edu/): `topicexplorer init --tokenizer inpho`
    - [ABI Human Brain Atlas](http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies): `topicexplorer init --tokenizer brain`
- Changed:
  - Massive load performance increases from upstream `vsm==0.4.0b1`.
  - [#136](http://github.com/inpho/topic-explorer/issues/136) - Rename master command from `vsm` to `topicexplorer`
- Deprecated:
  - `vsm` commands will be removed in v1.0.
- Removed:
  - Developer version of `vsm` from `dependency_links` in setup.py.
- Fixed:
  - [#116](http://github.com/inpho/topic-explorer/issues/116) - "vsm serve" should launch the browser - consistent with notebook and launch
  - [#122](http://github.com/inpho/topic-explorer/issues/122) - Number of seeds must be equal to number of processors
  - [#123](http://github.com/inpho/topic-explorer/issues/123) - update documentation to show PowerShell for windows
  - [#127](http://github.com/inpho/topic-explorer/issues/127) - typo in SEP url
  - [#128](http://github.com/inpho/topic-explorer/issues/128) - ini file is created relative to modeled dir, not pwd
  - [#132](http://github.com/inpho/topic-explorer/issues/132) - Handian corpus is saying "similarity of documents in the HandianCorpus to None"
  - [#134](http://github.com/inpho/topic-explorer/issues/134) - unicode being decoded in search box

## [1.0b88] - 2016-04-29
- Added:
  - Support for sentence-level modeling: `vsm init --sentences`
  - Default stop frequency argument: `vsm init --freq 5`
  - Quiet argument and nulls in `vsm prep`: `vsm prep -q`
  - Multi-process PDF conversion using `concurrent.futures` in `vsm init`.
- Changed:
  - Improve train memory performance from upstream changes in `vsm==0.4.0a26`
  - Improve prep memory performance from upstream changes in `vsm==0.4.0a23`
- Fixed:
  - Error in `vsm demo` (upstream)
  - Error in `vsm prep` with null values
  - Error in `vsm langspace`

## [1.0b79] - 2016-04-13
- Added:
  - Very basic support for Chinese word segmentation: `vsm langspace`
  - [#94](http://github.com/inpho/topic-explorer/issues/94) - Create generic fulltext file serving for pdfs and text files
  - [#97](http://github.com/inpho/topic-explorer/issues/97) - Add langdetect to `vsm prep` to use guesses for stopwords.
    - This change was reverted in
      [0048d60](https://github.com/inpho/topic-explorer/commit/0048d60944640da4932a590c9678bec92c283d34) due to performance issues.

- Changed:
  - Improve init and prep performance from upstream changes in `vsm==0.4.0a20`
  - No longer perform sentence mining by default. Significant speedup to `vsm
    init` for most use cases.
  - `label_module` semantics now use `init(viewer, config, args)`
  - [#113](http://github.com/inpho/topic-explorer/issues/113) - Topic view should default to normalized
- Fixed:
  - Fixed dynamic port switching
  - Fixed plus signs in doc_ids.
  - Fixed popover/search box z-index issue.
  - [#93](http://github.com/inpho/topic-explorer/issues/93) - continuation of training with fewer words / topic explorer can hang
  - [#107](http://github.com/inpho/topic-explorer/issues/107) - AP Demo text opening error
  - [#108](http://github.com/inpho/topic-explorer/issues/108) - Capture missing nltk libraries and suggest downloader command
  - [#111](http://github.com/inpho/topic-explorer/issues/111) - explorer error on TJBooks corpus
  - [#114](http://github.com/inpho/topic-explorer/issues/114) - vsm update on Windows fails clumsily when vsm.exe is running
  - [#115](http://github.com/inpho/topic-explorer/issues/115) - `vsm launch` should fail more gracefully.

## [1.0b60] - 2016-02-20
- Added:
  - Native benchmarking tools via `vsm -p` and `vsm -t`
  - ASCII histograms for `vsm prep` high and low frequency filters.
  - License badge for `README.md`
  - [#98](http://github.com/inpho/topic-explorer/issues/98) - Add `--dry-run` to help with automation in `vsm train`
- Changed:
  - Improve init performance from upstream changes in `vsm==0.4.0a11`
  - Migrated `vsm --version` to `vsm version`
  - [#105](http://github.com/inpho/topic-explorer/issues/105) - vsm init without .ini extension should auto-suggest
- Removed:
  - NP-hard graph coloring algorithm removed from topic explorer launch.
- Deprecated:
  - `vsm --version` will be removed in a future version.
- Fixed:
  - [#83](http://github.com/inpho/topic-explorer/issues/83) - "Close" button not appearing in reduced window
  - [#100](http://github.com/inpho/topic-explorer/issues/100) - Windows `vsm update` does not run
  - [#101](http://github.com/inpho/topic-explorer/issues/101) - Check if repo is on master branch in `vsm update`
  - [#102](http://github.com/inpho/topic-explorer/issues/102) - entering 0 for minimum word occurrence rate during vsm prep causes error

## [1.0b41] - 2016-02-02
- Added:
  - `vsm update` command.
  - `vsm --version` command.
  - `release.py` automation.
  - Notes in README.md on Bug Reports
- Changed:
  - Import upstream fixes via `vsm==0.4.0a8`
- Fixed:
  - `vsm init --unicode` fixed.
  - [#82](http://github.com/inpho/topic-explorer/issues/82) - Alphabetization not working
  - [#86](http://github.com/inpho/topic-explorer/issues/86) - Capitalization inconsistencies
  - [#89](http://github.com/inpho/topic-explorer/issues/89) - color map bug affecting browser launch


## 1.0b32 - 2016-01-20
- **Start of CHANGELOG.md**
- Added:
  - PDF file support
  - `--unicode`/`--decode` flags.
  - Progress bars
- Changed:
  - `vsm prep` now uses a single stoplist pass, using an in-place rather than out-of-place technique. Massive performance increase.



[Unreleased]: https://github.com/inpho/topic-explorer/compare/1.0b182...HEAD
[1.0b182]: https://github.com/inpho/topic-explorer/compare/1.0b159...1.0b182
[1.0b159]: https://github.com/inpho/topic-explorer/compare/1.0b146...1.0b159
[1.0b146]: https://github.com/inpho/topic-explorer/compare/1.0b134...1.0b146
[1.0b134]: https://github.com/inpho/topic-explorer/compare/1.0b121...1.0b134
[1.0b121]: https://github.com/inpho/topic-explorer/compare/1.0b111...1.0b121
[1.0b111]: https://github.com/inpho/topic-explorer/compare/1.0b107...1.0b111
[1.0b107]: https://github.com/inpho/topic-explorer/compare/1.0b106...1.0b107
[1.0b106]: https://github.com/inpho/topic-explorer/compare/1.0b88...1.0b106
[1.0b88]: https://github.com/inpho/topic-explorer/compare/1.0b79...1.0b88
[1.0b79]: https://github.com/inpho/topic-explorer/compare/1.0b60...1.0b79
[1.0b60]: https://github.com/inpho/topic-explorer/compare/1.0b41...1.0b60
[1.0b41]: https://github.com/inpho/topic-explorer/compare/1.0b32...1.0b41
