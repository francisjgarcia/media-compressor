# Changelog

## [v1.3.2](https://github.com/francisjgarcia/media-compressor/releases/v1.3.2) (2024-10-05)
* Merge pull request #20 from francisjgarcia/bug/video_dimensions_x_error [patch] @francisjgarcia ([#8023137](https://github.com/francisjgarcia/media-compressor/commit/8023137915d4b33896fb2af3120b8819b67a1ec4))
* fix(signal-handling): suppress ffmpeg errors on Ctrl + C interruption @francisjgarcia ([#364bbc2](https://github.com/francisjgarcia/media-compressor/commit/364bbc22db08a3727bddb3fb7400ed6c688e6b68))
* fix(video-dimensions): handle extra 'x' in video resolution parsing @francisjgarcia ([#14332c0](https://github.com/francisjgarcia/media-compressor/commit/14332c07f43583f1e5081edbee41ec367b02771f))


## [v1.3.1](https://github.com/francisjgarcia/media-compressor/releases/v1.3.1) (2024-10-05)
* Merge pull request #19 from francisjgarcia/bug/utf8_shared_folder [patch] @francisjgarcia ([#30d978e](https://github.com/francisjgarcia/media-compressor/commit/30d978e4d59efd917c0bc9efd7150049eb1f7377))
* bug(shared folder): fix utf8 characters of shared folders and rename mount function @francisjgarcia ([#9ae1c61](https://github.com/francisjgarcia/media-compressor/commit/9ae1c615e81259e377694c5c50281a256b6beec5))


## [v1.3.0](https://github.com/francisjgarcia/media-compressor/releases/v1.3.0) (2024-10-05)
* Merge pull request #18 from francisjgarcia/17-enhance-media-compressor-script-with-argparse-support @francisjgarcia ([#3da5dae](https://github.com/francisjgarcia/media-compressor/commit/3da5dae956d59cd996dda1bb49f8e78b6737783c))
* style: fix flake8 violations for line length and encoding @francisjgarcia ([#51bb7d3](https://github.com/francisjgarcia/media-compressor/commit/51bb7d354b650aa97b34c1701c8cd9a4a91615ad))
* feat: Enhance media compressor script with argparse support @francisjgarcia ([#a5b0c32](https://github.com/francisjgarcia/media-compressor/commit/a5b0c32299c3e13d7e853e81d17172ed4fedc290))


## [v1.2.2](https://github.com/francisjgarcia/media-compressor/releases/v1.2.2) (2024-09-28)
* [patch] Merge pull request #16 from francisjgarcia/8-progress-counter-exceeds-total-episode-count-when-multiple-episodes-are-in-a-single-file @francisjgarcia ([#6c12dfc](https://github.com/francisjgarcia/media-compressor/commit/6c12dfc61838ed7a2b0019b5ac382cf49ef08ad9))
* bug(series): Progress counter exceeds total episode count when multiple episodes are in a single file @francisjgarcia ([#1c6d574](https://github.com/francisjgarcia/media-compressor/commit/1c6d574f8515bde4e349e11c0865cefc7e3e5149))


## [v1.2.1](https://github.com/francisjgarcia/media-compressor/releases/v1.2.1) (2024-09-28)
* [patch] Merge pull request #15 from francisjgarcia/bug/ffprobe_duration @francisjgarcia ([#fa6c306](https://github.com/francisjgarcia/media-compressor/commit/fa6c306c59ad53160ad034096fff6f6fe08c9a09))
* bug(files): Fix bug error for ffmpeg duration @francisjgarcia ([#1266783](https://github.com/francisjgarcia/media-compressor/commit/12667830c2ccca0e1be26ac049a9ef761153e9a4))
* [patch] Merge pull request #14 from francisjgarcia/bug/alphanumeric_characters_title @francisjgarcia ([#7cef678](https://github.com/francisjgarcia/media-compressor/commit/7cef6787b4b1eef840d5a036eae32eb86e5f2af4))
* bug(files): If the title has alphanumeric characters such as a single quote, the file name may not be read correctly @francisjgarcia ([#783ddb6](https://github.com/francisjgarcia/media-compressor/commit/783ddb6eee4a7d584dea0f2ddf737611c65241d2))


## [v1.2.0](https://github.com/francisjgarcia/media-compressor/releases/v1.2.0) (2024-09-27)
* (patch) Merge pull request #13 from francisjgarcia/12-next-movie-in-compression-loop-is-saved-inside-previous-movies-folder-instead-of-destination-root-folder @francisjgarcia ([#785195f](https://github.com/francisjgarcia/media-compressor/commit/785195fce88a5e190bb7df29b63aada60b13025c))
* bug(movies): fix incorrect output path for compressed movies in loop @francisjgarcia ([#a83948d](https://github.com/francisjgarcia/media-compressor/commit/a83948d67e5a35fbf722dbf90d02909512a4a183))


## [v1.1.0](https://github.com/francisjgarcia/media-compressor/releases/v1.1.0) (2024-09-27)
* Merge pull request #11 from francisjgarcia/4-add-ffmpeg-progress-bar @francisjgarcia ([#4351f79](https://github.com/francisjgarcia/media-compressor/commit/4351f7929c07fa05fcb675a9f119d2b4904705ed))
* feat: Add ffmpeg progress bar @francisjgarcia ([#2524b8f](https://github.com/francisjgarcia/media-compressor/commit/2524b8f3a82769215b32d7f13ad71831557cd4da))


## [v1.0.0](https://github.com/francisjgarcia/media-compressor/releases/v1.0.0) (2024-09-27)
